import snowflake.connector


def set_snowflake_connection(config):
    return snowflake.connector.connect(
        user=config['snowflakeUserName'],
        password=config['snowflakePassword'],
        account=config['snowflakeAccountName'],
    )

def handle_pixel_request(config, search_criteria):
    conn = None
    cursor = None
    try:
        # Connect to Snowflake
        conn = set_snowflake_connection(config)
        cursor = conn.cursor()

        query = search_criteria['query']
        cursor.execute(query)

        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)
    finally:
        # Close cursor and connection in finally block to ensure they're always closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()