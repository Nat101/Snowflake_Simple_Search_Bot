/*
STEP 2: Create a stage to store files.
Download the AirBnB listings dataset hosted on Huggingface:
https://drive.google.com/file/d/1mZwfcB4goPiyCaYe34gTE1Er8-9-hdGY/view?usp=sharing. 
Upload airbnb_embeddings.json to the stage.
Load the staged file into a new table AIRBNB_LISTINGS
Note in the Load Data into Table dialog, make the following adjustments:
1. Uncheck Load as a single variant column?
2. Uncheck the image_embeddings, images, and text_embeddings columns, since those do not apply to this tutorial. 
3. Adjust the datatype of the amenities field to be ARRAY type.
*/

USE DATABASE CORTEX_SEARCH_TUTORIAL_DB;
USE SCHEMA PUBLIC;

CREATE OR REPLACE STAGE AIRBNB_STAGE
    DIRECTORY = (ENABLE = TRUE)
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');