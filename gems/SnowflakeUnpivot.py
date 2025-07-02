from dataclasses import dataclass

# Base classes from Prophecy framework
from collections import defaultdict
from prophecy.cb.sql.Component import *
from prophecy.cb.sql.MacroBuilderBase import *
from prophecy.cb.ui.uispec import *

# Define the custom gem spec for unpivoting in Snowflake
class SnowflakeUnpivot(MacroSpec):
    name: str = "SnowflakeUnpivot"
    projectName: str = "br_framework"
    category: str = "Transform"
    minNumOfInputPorts: int = 1

    # Macro properties definition using dataclass
    @dataclass(frozen=True)
    class SnowflakeUnpivotProperties(MacroProperties):
        relation_name: List[str] = field(default_factory=list)   # Source table name(s)
        field_name: Optional[str] = None                         # Name of column that stores unpivoted column names
        value_name: Optional[str] = None                         # Name of column that stores unpivoted values
        cast_to: Optional[str] = "string"                        # Data type to cast values to
        exclude: List[str] = field(default_factory=list)         # Columns to keep (not unpivot)
        remove: List[str] = field(default_factory=list)          # Columns to drop entirely
        where_condition: str = ""                                # Optional WHERE clause filter

    # Define the UI for configuring the macro
    def dialog(self) -> Dialog:
        data_type_select_box = (
            SelectBox("Data Type (Casts all unpivoted values to this type)")
                .addOption("string", "string")
                .bindProperty("cast_to")
        )

        return Dialog("Macro").addElement(
            ColumnsLayout(gap="1rem", height="100%")
            .addColumn(Ports(), "content")
            .addColumn(StackLayout()
                .addElement(
                    SchemaColumnsDropdown("Key Columns (Columns you want to keep in the output table, not unpivot (default: ['ID']))")
                        .withMultipleSelection()
                        .bindSchema("component.ports.inputs[0].schema")
                        .bindProperty("exclude")
                        .showErrorsFor("exclude")
                )
                .addElement(
                    SchemaColumnsDropdown("Exclude Columns (Additional columns to exclude from unpivoting (empty by default))")
                        .withMultipleSelection()
                        .bindSchema("component.ports.inputs[0].schema")
                        .bindProperty("remove")
                        .showErrorsFor("remove")
                )
                .addElement(
                    TextBox("Field column name")
                        .bindPlaceholder("Name of the new column that will hold the original column names (default: key)")
                        .bindProperty("field_name")
                )
                .addElement(
                    TextBox("Value column came")
                        .bindPlaceholder("Name of the new column that will hold the values (default: value)")
                        .bindProperty("value_name")
                )
                .addElement(data_type_select_box)
                .addElement(
                    TextBox("Where clause (Optional)")
                        .bindPlaceholder("Optional WHERE clause filter before unpivoting (eg: customer_id > 10)")
                        .bindProperty("where_condition")
                )
            )
        )

    # Basic validator that can be extended later
    def validate(self, context: SqlContext, component: Component) -> List[Diagnostic]:
        return super().validate(context, component)

    # Update the component state when configuration changes
    def onChange(self, context: SqlContext, oldState: Component, newState: Component) -> Component:
        relation_name = self.get_relation_names(component, context)
        return replace(newState, properties=replace(newState.properties, relation_name=relation_name))

    # Generate macro SQL code from component properties
    def apply(self, props: SnowflakeUnpivotProperties) -> str:
        exclude_list = [col.upper() for col in props.exclude if col != ""]
        remove_list  = [col.upper() for col in props.remove if col != ""]

        try:
            table_name: str = str(props.relation_name[0])
        except:
            table_name = ""

        field_name = "KEY" if props.field_name in (None, "") else props.field_name
        value_name = "VALUE" if props.value_name in (None, "") else props.value_name
        cast_to    = "string" if props.cast_to in (None, "") else props.cast_to

        resolved_macro_name = f"{self.projectName}.{self.name}"

        arguments = [
            f"ref('{table_name}')",
            f"'{field_name}'",
            f"'{value_name}'",
            f"'{cast_to}'",
            str(exclude_list),
            str(remove_list),
            f"\"{props.where_condition}\""
        ]

        params = ",".join(arguments)
        return f"{{{{ {resolved_macro_name}({params}) }}}}"

    # Resolve upstream relation names based on graph connections
    def get_relation_names(self, component: Component, context: SqlContext):
        all_upstream_nodes = []
        for inputPort in component.ports.inputs:
            upstreamNode = None
            for connection in context.graph.connections:
                if connection.targetPort == inputPort.id:
                    upstreamNodeId = connection.source
                    upstreamNode = context.graph.nodes.get(upstreamNodeId)
            all_upstream_nodes.append(upstreamNode)

        relation_name = []
        for upstream_node in all_upstream_nodes:
            if upstream_node is None or upstream_node.label is None:
                relation_name.append("")
            else:
                relation_name.append(upstream_node.label)

        return relation_name

    # Deserialize properties from saved component config
    def loadProperties(self, properties: MacroProperties) -> PropertiesType:
        parametersMap = self.convertToParameterMap(properties.parameters)
        return SnowflakeUnpivot.SnowflakeUnpivotProperties(
            relation_name=parametersMap.get('relation_name'),
            field_name=parametersMap.get('field_name'),
            value_name=parametersMap.get('value_name'),
            cast_to=parametersMap.get('cast_to'),
            exclude=json.loads(parametersMap.get('exclude').replace("'", '"')),
            remove=json.loads(parametersMap.get('remove').replace("'", '"')),
            where_condition=parametersMap.get('where_condition')
        )

    # Serialize properties for saving
    def unloadProperties(self, properties: PropertiesType) -> MacroProperties:
        return BasicMacroProperties(
            macroName=self.name,
            projectName=self.projectName,
            parameters=[
                MacroParameter("relation_name", str(properties.relation_name)),
                MacroParameter("field_name", str(properties.field_name)),
                MacroParameter("value_name", str(properties.value_name)),
                MacroParameter("cast_to", str(properties.cast_to)),
                MacroParameter("exclude", json.dumps(properties.exclude)),
                MacroParameter("remove", json.dumps(properties.remove)),
                MacroParameter("where_condition", properties.where_condition)
            ],
        )

    # Update port slug when graph changes
    def updateInputPortSlug(self, component: Component, context: SqlContext):
        relation_name = self.get_relation_names(component, context)
        return replace(component, properties=replace(component.properties, relation_name=relation_name))