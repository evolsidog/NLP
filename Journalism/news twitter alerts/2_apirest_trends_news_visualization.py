import json
from st_aggrid import AgGrid, GridUpdateMode, JsCode, ColumnsAutoSizeMode
import streamlit as st

import pandas as pd

# with open('tweets_info.json', mode='r', encoding='utf-8') as f:
#     trend_tweets_info = json.load(f)
    # print(trend_tweets_info)

trend_df = pd.read_json('tweets_info.json')

# 10 trending topics (dict), each one has 10 tweets (list) and each one tweet has 8 fields (dict): 
print(trend_df.keys()) # trending topics

# create visualization and wordcloud. Streamlit table

# 1) Convert json to dataframe
print(len(trend_df['El Gobierno']))
print(trend_df['El Gobierno'][0].keys())

# first start with table 10x10, column is trending topic, and each cell is the relevant tweet with its information
# trend_df = pd.DataFrame.from_dict(trend_tweets_info, orient='index')
trend_df = trend_df.transpose()

trend_df = trend_df.applymap(lambda x: [str(key) + ": " + str(value) + "\n" for key, value in x.items()])
trend_df.columns = ["Tweet " + str(col) for col in trend_df.columns]
# for col in trend_df.columns:
#     trend_df[col] = trend_df[col].apply(lambda x: pd.json_normalize(x))

trend_df = trend_df.reset_index().rename(columns={'index':'trending topic'})

# st.dataframe(trend_df, use_container_width=True)


# def generate_column_defs(column_name):
#     return{
#             "field": column_name,
#             "cellRenderer": "agGroupCellRenderer",
#         }

# gridOptions = {
#     # enable Master / Detail
#     "masterDetail": True,
#     "rowSelection": "single",
#     # the first Column is configured to use agGroupCellRenderer
#     "columnDefs": [
#         {"field": "trending topic"},
#         generate_column_defs("Tweet 0"),
#         generate_column_defs("Tweet 1"),
#         generate_column_defs("Tweet 2"),
#         generate_column_defs("Tweet 3"),
#         generate_column_defs("Tweet 4"),
#         generate_column_defs("Tweet 5"),
#         generate_column_defs("Tweet 6"),
#         generate_column_defs("Tweet 7"),
#         generate_column_defs("Tweet 8"),
#         generate_column_defs("Tweet 9"),
#     ],
#     "defaultColDef": {
#         "flex": 1,
#     },
#     # provide Detail Cell Renderer Params
#     "detailCellRendererParams": {
#         # provide the Grid Options to use on the Detail Grid
#         "detailGridOptions": {
#             "columnDefs": [
#                 {"field": "text"},
#                 {"field": "creation_date"},
#                 {"field": "url"},
#                 {"field": "metrics"},
#                 {"field": "username"},
#                 {"field": "name"},
#                 {"field": "ner_entities"},
#                 {"field": "context_annotations"},
#             ],
#             "defaultColDef": {
#                 "sortable": True,
#                 "flex": 1,
#             },
#         },
#         # get the rows for each Detail Grid
#         "getDetailRowData": JsCode(
#             """function (params) {
#                 console.log(params);
#                 params.successCallback(params.data.callRecords);
#     }"""
#         ).js_code,
#     },
# }

AgGrid(
    trend_df,
    # gridOptions=gridOptions,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=True,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
)