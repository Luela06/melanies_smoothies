import streamlit as st
from snowflake.snowpark.functions import col

# Assuming you have a secure way to establish a Snowflake connection
cnx = st.session()  # Assuming the connection is established elsewhere

# Streamlit App UI
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("""Choose the fruits you want in your Custom Smoothie!""")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

# Fetch fruit options from Snowflake
my_dataframe = cnx.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Allow user to select ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'].tolist(),  # Use a list of fruit names
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Create comma-separated string

    # Loop through chosen ingredients
    for fruit_chosen in ingredients_list:
        search_on = my_dataframe.loc[my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')

        try:
            smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
            smoothiefroot_response.raise_for_status()  # Raise an exception for non-200 status codes
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching nutrition information for {fruit_chosen}: {e}")

    # Order submission
    if st.button('Submit Order'):
        try:
            my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                               values ('{ingredients_string}', '{name_on_order}')"""
            cnx.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:  # Catch general exceptions for database errors
            st.error(f"Error submitting order: {e}")
