import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
    
def create_table():
    print("DB가 생성됩니다.")
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = f"CREATE TABLE IF NOT EXISTS product (id INTEGER PRIMARY KEY, title TEXT, price TEXT, option_type TEXT, option_val TEXT, is_soldout BOOLEAN, link TEXT)"
    cursor.execute(sql)
    conn.commit()
    conn.close()
    
def load_all_product() -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM product"
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return rows

def load_product_by_id(product_id:int) -> sqlite3.Row:
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = f"SELECT * FROM product WHERE id={product_id}"
    cursor.execute(sql)
    product = cursor.fetchone()
    conn.close()
    return product

def add_product(title, price, option_type, option_val, is_soldout, link) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = f"INSERT INTO product (title, price, option_type, option_val, is_soldout, link) VALUES ('{title}', '{price}', '{option_type}', '{option_val}', {is_soldout}, '{link}')"
    print(sql)
    cursor.execute(sql) # 실행해
    conn.commit() # 반영해
    product_id = cursor.lastrowid
    conn.close()
    return product_id
    
def delete_product_by_id(product_id:int):
    print("delete_product_by_id, ID: ", product_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = f"DELETE FROM product WHERE id = {product_id}"
    cursor.execute(sql)
    conn.commit()
    conn.close()
    
# def update_product_by_id(product_id:int, new_is_soldout:bool):
#     print("update_product_by_id, ID: ", product_id)
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     sql = f"UPDATE product SET option_val = is_soldout = {new_is_soldout} WHERE id = {product_id}"
#     cursor.execute(sql)
#     conn.commit()
#     conn.close()
    
def update_product_by_id(product_id, new_title=None, new_price=None, new_option_type=None, new_option_val=None, new_is_soldout=None, new_link=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 업데이트할 필드 및 해당 값 목록 생성
    update_fields = []
    if new_title is not None:
        update_fields.append(f"title = '{new_title}'")
    if new_price is not None:
        update_fields.append(f"price = '{new_price}'")
    if new_option_type is not None:
        update_fields.append(f"option_type = '{new_option_type}'")
    if new_option_val is not None:
        update_fields.append(f"option_val = '{new_option_val}'")
    if new_is_soldout is not None:
        update_fields.append(f"is_soldout = {new_is_soldout}")
    if new_link is not None:
        update_fields.append(f"link = '{new_link}'")

    # SQL UPDATE 쿼리 생성
    sql = f"UPDATE product SET {', '.join(update_fields)} WHERE id = ?"
    values = (product_id,)
    cursor.execute(sql, values)
    conn.commit()
    conn.close()



    
