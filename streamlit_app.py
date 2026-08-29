# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests  

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw: {st.__version__}")
st.write(
  """Choose the fruits you want in your smoothie!
  """
)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the snowspark dataframe to pandas
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

name_on_order = st.text_input('Please input your name:')
st.write('The name on your smoothie will be:', name_on_order)

ingredient_list = st.multiselect(
    label='Choose up to 5 ingredients',
    options = my_dataframe,
    max_selections=5
)

if ingredient_list:
    ingredients_string = ''

    for fruit_chosen in ingredient_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")  
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    
    time_to_insert = st.button('Submit order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")






