from dotenv import load_dotenv
import os
import MySQLdb
import certifi

# Function to execute a given SQL command and return the results
def execute_sql_command(sql_command):
    # Load environment variables from the .env file
    load_dotenv()

    ca = certifi.where()
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')

    print(f'Connecting to the database {db_name} on {db_host} as {db_user}...')
    
    try:
        # Connect to the database
        connection = MySQLdb.connect(
            host=db_host,
            user=db_user,
            passwd=db_password,
            db=db_name,
            autocommit=True,
            ssl_mode="VERIFY_IDENTITY",
            ssl={"ca": ca}
        )

        # Create a cursor to interact with the database
        cursor = connection.cursor()

        # Execute the given SQL command
        cursor.execute(sql_command)

        # Fetch all the rows
        results = cursor.fetchall()

        # Return the results
        return results

    except MySQLdb.Error as e:
        print("MySQL Error:", e)
        return None

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# Example usage
if __name__ == "__main__":
    sql_command = "SHOW TABLES"  # Example SQL command
    results = execute_sql_command(sql_command)
    if results:
        print("Results:")
        for result in results:
            print(result[0])
    else:
        print("No results or an error occurred.")
