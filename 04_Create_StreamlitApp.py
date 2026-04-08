# Import python packages
import streamlit as st
from snowflake.core import Root
from snowflake.snowpark.context import get_active_session

# Constants
DB = "cortex_search_tutorial_db"
SCHEMA = "public"
SERVICE = "airbnb_svc"
BASE_TABLE = "cortex_search_tutorial_db.public.airbnb_listings"
ARRAY_ATTRIBUTES = {"AMENITIES"}


def get_column_specification():
    """
    This function retrieves information about the attributes available in the search service and stores them in Streamlit state.
    """
    session = get_active_session()
    search_service_result = session.sql(f"DESC CORTEX SEARCH SERVICE {DB}.{SCHEMA}.{SERVICE}").collect()[0]
    st.session_state.attribute_columns = search_service_result.attribute_columns.split(",")
    st.session_state.search_column = search_service_result.search_column
    st.session_state.columns = search_service_result.columns.split(",")

def init_layout():
    """
    This function sets up the header and intro of the page
    """
    st.title("Cortex AI Search")
    st.markdown(f"Querying service: `{DB}.{SCHEMA}.{SERVICE}`".replace('"', ''))

def query_cortex_search_service(query, filter={}):
    """
    This function queries the cortex search service in the session state and returns a list of results.
    """
    session = get_active_session()
    cortex_search_service = (
        Root(session)
        .databases[DB]
        .schemas[SCHEMA]
        .cortex_search_services[SERVICE]
    )
    context_documents = cortex_search_service.search(
        query,
        columns=st.session_state.columns,
        filter=filter,
        limit=st.session_state.limit)
    return context_documents.results

@st.cache_data
def distinct_values_for_attribute(col_name, is_array_attribute=False):
    """
    This function determines which values are possible for each filterable attribute to populate the dropdown menus.
    """
    session = get_active_session()
    if is_array_attribute:
        values = session.sql(f'''
        SELECT DISTINCT value FROM {BASE_TABLE},
        LATERAL FLATTEN(input => {col_name})
        ''').collect()
    else:
        values = session.sql(f"SELECT DISTINCT {col_name} AS VALUE FROM {BASE_TABLE}").collect()
    return [ x["VALUE"].replace('"', "") for x in values ]

def init_search_input():
    """
    This function initializes inputs for the search query.
    """
    st.session_state.query = st.text_input("Query")

def init_limit_input():
    """
    This function limits number of results.
    """
    st.session_state.limit = st.number_input("Limit", min_value=1, value=5)

def init_attribute_selection():
    """
    This function selects the attribute filters.
    """
    st.session_state.attributes = {}
    for col in st.session_state.attribute_columns:
        is_multiselect = col in ARRAY_ATTRIBUTES
        st.session_state.attributes[col] = st.multiselect(
            col,
            distinct_values_for_attribute(col, is_array_attribute=is_multiselect)
        )

def display_search_results(results):
    """
    This function formats search results into Markdown elements displayed in the results page.
    """
    st.subheader("Search results")
    for i, result in enumerate(results):
        result = dict(result)
        container = st.expander(f"[Result {i+1}]", expanded=True)

        # Add the result text.
        container.markdown(result[st.session_state.search_column])

        # Add the attributes.
        for column, column_value in sorted(result.items()):
            if column == st.session_state.search_column:
                continue
            container.markdown(f"**{column}**: {column_value}")

def create_filter_object(attributes):
    """
    This function processes selected filter attributes from the Streamlit form into 
    the right objects to be used by the Python library for querying Cortex Search.
    """
    and_clauses = []
    for column, column_values in attributes.items():
        if len(column_values) == 0:
            continue
        if column in ARRAY_ATTRIBUTES:
            for attr_value in column_values:
                and_clauses.append({"@contains": { column: attr_value }})
        else:
            or_clauses = [{"@eq": {column: attr_value}} for attr_value in column_values]
            and_clauses.append({"@or": or_clauses })

    return {"@and": and_clauses} if and_clauses else {}


def main():
    init_layout()
    get_column_specification()
    init_attribute_selection()
    init_limit_input()
    init_search_input()

    if not st.session_state.query:
        return
    results = query_cortex_search_service(
        st.session_state.query,
        filter = create_filter_object(st.session_state.attributes)
    )
    display_search_results(results)


if __name__ == "__main__":
    st.set_page_config(page_title="Cortex AI Search and Summary", layout="wide")
    main()