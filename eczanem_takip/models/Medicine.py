import MySQLdb

class ActiveIngredient:
    def __init__(self, id, name, amount):
        self.id = id
        self.name = name
        self.amount = amount

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount
        }

class Medicine:
    def __init__(self, id, public_number, atc_code, report_type, name, brand, form, barcode, equivalent_medicine_group):
        self.id = id
        self.public_number = public_number
        self.atc_code = atc_code
        self.report_type = report_type
        self.name = name
        self.brand = brand
        self.form = form
        self.barcode = barcode
        self.equivalent_medicine_group = equivalent_medicine_group

    def serialize(self):
        return {
            'id': self.id,
            'public_number': self.public_number,
            'atc_code': self.atc_code,
            'report_type': self.report_type,
            'name': self.name,
            'brand': self.brand,
            'form': self.form,
            'barcode': self.barcode,
            'equivalent_medicine_group': self.equivalent_medicine_group
        }

    @staticmethod
    def get_all(connection):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM medicine")
        rows = cursor.fetchall()
        cursor.close()
        return [Medicine(**row) for row in rows]

    @staticmethod
    def get_by_id(connection, medicine_id):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM medicine WHERE id = %s", (medicine_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Medicine(**row)
        return None

    @staticmethod
    def get_by_name_or_barcode(connection, identifier):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM medicine WHERE name = %s OR barcode = %s", (identifier, identifier))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Medicine(**row)
        return None

    @staticmethod
    def add(connection, medicine):
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO medicine (public_number, atc_code, report_type, name, brand, form, barcode, equivalent_medicine_group)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (medicine.public_number, medicine.atc_code, medicine.report_type, medicine.name, medicine.brand,
              medicine.form, medicine.barcode, medicine.equivalent_medicine_group))
        connection.commit()
        medicine_id = cursor.lastrowid
        cursor.close()
        return medicine_id

    @staticmethod
    def update(connection, medicine):
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE medicine SET public_number = %s, atc_code = %s, report_type = %s, name = %s, brand = %s, form = %s, 
            barcode = %s, equivalent_medicine_group = %s WHERE id = %s
        """, (medicine.public_number, medicine.atc_code, medicine.report_type, medicine.name, medicine.brand,
              medicine.form, medicine.barcode, medicine.equivalent_medicine_group, medicine.id))
        connection.commit()
        cursor.close()

    @staticmethod
    def delete(connection, medicine_id):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM medicine WHERE id = %s", (medicine_id,))
        connection.commit()
        cursor.close()

    @staticmethod
    def record_sale_by_name_or_barcode(connection, user_id, identifier, customer_name, sale_date, quantity):
        cursor = connection.cursor()
        try:
            medicine = Medicine.get_by_name_or_barcode(connection, identifier)
            if not medicine:
                raise Exception("Medicine not found")

            cursor.execute("""
                INSERT INTO medicine_sales (user_id, medicine_id, customer_name, sale_date, quantity)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, medicine.id, customer_name, sale_date, quantity))

            # Decrement the stock
            cursor.execute("""
                UPDATE medicine_stock
                SET quantity = quantity - %s
                WHERE medicine_id = %s AND user_id = %s AND quantity >= %s
                ORDER BY expiry_date ASC
                LIMIT 1
            """, (quantity, medicine.id, user_id, quantity))

            if cursor.rowcount == 0:
                raise Exception("Not enough stock to complete the sale")

            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()



    @staticmethod
    def get_active_ingredient_by_name(connection, name):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM active_ingredient WHERE name = %s", (name,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return ActiveIngredient(**row)
        return None

    @staticmethod
    def add_active_ingredient(connection, name, amount):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO active_ingredient (name, amount) VALUES (%s, %s)", (name, amount))
        connection.commit()
        return cursor.lastrowid

    @staticmethod
    def add_medicine_active_ingredient(connection, medicine_id, active_ingredient_id):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO medicine_active_ingredient (medicine_id, active_ingredient_id) VALUES (%s, %s)",
                       (medicine_id, active_ingredient_id))
        connection.commit()


    @staticmethod
    def get_active_ingredients_for_medicine(connection, medicine_id):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT ai.id, ai.name, ai.amount 
            FROM active_ingredient ai
            JOIN medicine_active_ingredient mai ON ai.id = mai.active_ingredient_id
            WHERE mai.medicine_id = %s
        """, (medicine_id,))
        rows = cursor.fetchall()
        cursor.close()
        return [ActiveIngredient(id=row[0], name=row[1], amount=row[2]) for row in rows]

    @staticmethod
    def update_active_ingredient(connection, ingredient):
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE active_ingredient SET name = %s, amount = %s WHERE id = %s
        """, (ingredient.name, ingredient.amount, ingredient.id))
        connection.commit()
        cursor.close()

    @staticmethod
    def delete_active_ingredient(connection, ingredient_id):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM active_ingredient WHERE id = %s", (ingredient_id,))
        connection.commit()
        cursor.close()

    @staticmethod
    def get_active_ingredient_by_id(connection, ingredient_id):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM active_ingredient WHERE id = %s", (ingredient_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return ActiveIngredient(**row)
        return None

    @staticmethod
    def get_all_active_ingredients( connection):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM active_ingredient")
        rows = cursor.fetchall()
        cursor.close()
        return [ActiveIngredient(id=row['id'], name=row['name'], amount=row['amount']) for row in rows]

    @classmethod
    def remove_all_active_ingredients(cls, connection, medicine_id):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM medicine_active_ingredient WHERE medicine_id = %s", (medicine_id,))
        connection.commit()
        cursor.close()