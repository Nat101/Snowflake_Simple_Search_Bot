/*
Step 4: Create a Cortex Search Service on the table to allow you to search

The ON parameter specifies the column for queries to search over.
In this example, it’s listing_text, which is generated in the source query as
a concatenation of several text columns in the base table.

The ATTRIBUTES parameter specifies the columns that you will be able to filter search results on. 
This example filters on room_type and amenities when issuing 
queries to the listing_text column.

The TARGET_LAG parameter specifies the desired freshness of the search service. 
This example specifies to keep the service no more than '1 hour' behind the source table AIRBNB_LISTINGS.

The AS field defines the source table for the service. This example concatenates 
several text columns in the original table into the search column listing_text so that 
queries can search over multiple fields.
*/

USE DATABASE CORTEX_SEARCH_TUTORIAL_DB;
USE SCHEMA PUBLIC;

CREATE OR REPLACE CORTEX SEARCH SERVICE AIRBNB_SVC
ON LISTING_TEXT
ATTRIBUTES ROOM_TYPE, AMENITIES
WAREHOUSE = CORTEX_SEARCH_TUTORIAL_WH
TARGET_LAG = '1 hour'
AS
    SELECT
        ROOM_TYPE,
        AMENITIES,
        PRICE,
        CANCELLATION_POLICY,
        ('Summary\n\n' || SUMMARY || '\n\n\nDescription\n\n' || DESCRIPTION || '\n\n\nSpace\n\n' || SPACE) AS LISTING_TEXT
    FROM CORTEX_SEARCH_TUTORIAL_DB.PUBLIC.AIRBNB_LISTINGS;