import MySQLdb


class Medicine:
    def __init__(self, id, public_number, name, brand, form, barcode, equivalent_medicine_group):
        self.id = id
        self.public_number = public_number
        self.name = name
        self.brand = brand
        self.form = form
        self.barcode = barcode
        self.equivalent_medicine_group = equivalent_medicine_group

    def serialize(self):
        return {
            'id': self.id,
            'public_number': self.public_number,
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
    def add(connection, medicine):
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO medicine (public_number, name, brand, form,  barcode, equivalent_medicine_group)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (medicine.public_number, medicine.name, medicine.brand, medicine.form, medicine.barcode,
              medicine.equivalent_medicine_group))
        connection.commit()
        cursor.close()

    @staticmethod
    def update(connection, medicine):
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE medicine SET public_number = %s, name = %s, brand = %s, form = %s, 
             barcode = %s, equivalent_medicine_group = %s WHERE id = %s
        """, (medicine.public_number, medicine.name, medicine.brand, medicine.form, medicine.barcode,
              medicine.equivalent_medicine_group, medicine.id))
        connection.commit()
        cursor.close()

    @staticmethod
    def delete(connection, medicine_id):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM medicine WHERE id = %s", (medicine_id,))
        connection.commit()
        cursor.close()


class ActiveIngredient:
    def __init__(self, id, name, amount):
        self.id = id
        self.name = name
        self.amount = amount

    @staticmethod
    def get_all(connection):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM active_ingredient")
        rows = cursor.fetchall()
        cursor.close()
        return [ActiveIngredient(**row) for row in rows]

    @staticmethod
    def get_by_id(connection, ingredient_id):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM active_ingredient WHERE id = %s", (ingredient_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return ActiveIngredient(**row)
        return None

    @staticmethod
    def add(connection, ingredient):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO active_ingredient (name, amount) VALUES (%s, %s)",
                       (ingredient.name, ingredient.amount))
        connection.commit()
        cursor.close()

    @staticmethod
    def update(connection, ingredient):
        cursor = connection.cursor()
        cursor.execute("UPDATE active_ingredient SET name = %s, amount = %s WHERE id = %s",
                       (ingredient.name, ingredient.amount, ingredient.id))
        connection.commit()
        cursor.close()

    @staticmethod
    def delete(connection, ingredient_id):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM active_ingredient WHERE id = %s", (ingredient_id,))
        connection.commit()
        cursor.close()


class Supplier:
    def __init__(self, id, name, contact_info):
        self.id = id
        self.name = name
        self.contact_info = contact_info

    @staticmethod
    def get_all(connection):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM supplier")
        rows = cursor.fetchall()
        cursor.close()
        return [Supplier(**row) for row in rows]

    @staticmethod
    def get_by_id(connection, supplier_id):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM supplier WHERE id = %s", (supplier_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Supplier(**row)
        return None

    @staticmethod
    def add(connection, supplier):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO supplier (name, contact_info) VALUES (%s, %s)",
                       (supplier.name, supplier.contact_info))
        connection.commit()
        cursor.close()

    @staticmethod
    def update(connection, supplier):
        cursor = connection.cursor()
        cursor.execute("UPDATE supplier SET name = %s, contact_info = %s WHERE id = %s",
                       (supplier.name, supplier.contact_info, supplier.id))
        connection.commit()
        cursor.close()

    @staticmethod
    def delete(connection, supplier_id):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM supplier WHERE id = %s", (supplier_id,))
        connection.commit()
        cursor.close()


class MedicineStock:
    def __init__(self, id, medicine_id, supplier_id, user_id, expiry_date, quantity, storage_conditions):
        self.id = id
        self.medicine_id = medicine_id
        self.supplier_id = supplier_id
        self.user_id = user_id
        self.expiry_date = expiry_date
        self.quantity = quantity
        self.storage_conditions = storage_conditions

    @staticmethod
    def get_all(connection):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM medicine_stock")
        rows = cursor.fetchall()
        cursor.close()
        return [MedicineStock(**row) for row in rows]

    @staticmethod
    def get_by_id(connection, stock_id):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM medicine_stock WHERE id = %s", (stock_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return MedicineStock(**row)
        return None

    @staticmethod
    def add(connection, stock):
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO medicine_stock (medicine_id, supplier_id, user_id, expiry_date, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """, (stock.medicine_id, stock.supplier_id, stock.user_id,
              stock.expiry_date, stock.quantity, stock.storage_conditions))
        connection.commit()
        cursor.close()

    @staticmethod
    def update(connection, stock):
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE medicine_stock SET medicine_id = %s, supplier_id = %s, user_id = %s,
            expiry_date = %s, quantity = %s WHERE id = %s
        """, (stock.medicine_id, stock.supplier_id, stock.user_id,
              stock.expiry_date, stock.quantity, stock.storage_conditions, stock.id))
        connection.commit()
        cursor.close()

    @staticmethod
    def delete(connection, stock_id):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM medicine_stock WHERE id = %s", (stock_id,))
        connection.commit()
        cursor.close()
