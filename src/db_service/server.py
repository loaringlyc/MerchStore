import grpc
from concurrent import futures
from pprint import pprint
import time
import os

from db_proto import db_pb2
from db_proto import db_pb2_grpc

import psycopg2
from psycopg2 import pool

from google.protobuf import empty_pb2
from google.protobuf.timestamp_pb2 import Timestamp

# Create a SimpleConnectionPool for a single-threaded application
simple_pool = psycopg2.pool.SimpleConnectionPool(
  minconn=1,
  maxconn=10,
  user="dncc",
  # maybe password need to be read from environment variable for security issue
  password="dncc",
  host="localhost",
  port="5432",
  database="goodsstore"
)

class ProductServiceServicer(db_pb2_grpc.ProductServiceServicer):
    def CreateProduct(self, request, context):
        print(f"Received CreateProduct request for name: {request.name}")

        # checking by the server
        if not request.name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Product name is required.")
            return db_pb2.Product()
        if request.price < 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Product price cannot be negative.")
            return db_pb2.Product()
        if request.stock < 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Product stock cannot be negative.")
            return db_pb2.Product()
        
        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                query = """ 
                    INSERT INTO products (name, description, category, price, slogan, stock)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, name, description, category, price, slogan, stock, created_at;
                """ # use RETURNING *, which is efficient
                cursor.execute(query, (
                    request.name,
                    request.description,
                    request.category,
                    request.price,
                    request.slogan,
                    request.stock
                ))

                new_row = cursor.fetchone()
                conn.commit() # save chang
                if new_row is None:
                    raise Exception("Failed to retrieve the new product after insertion.")
                
                product = db_pb2.Product(
                    id=new_row[0],
                    name=new_row[1],
                    description=new_row[2],
                    category=new_row[3],
                    price=float(new_row[4]),
                    slogan=new_row[5],
                    stock=new_row[6]
                )

                if new_row[7] is not None:
                    ts = Timestamp()
                    ts.FromDatetime(new_row[7])
                    product.created_at.CopyFrom(ts)
                
                print(f"Successfully created product with ID: {product.id}")
                return product
            
        except Exception as e:
            pprint(f"An unexpected error occurred in CreateProduct: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"An unexpected error occurred: {e}")
            return db_pb2.Product()
        finally:
            if conn:
                simple_pool.putconn(conn)

    def GetProduct(self, request, context):
        print(f"Received GetProduct request for ID: {request.id}")
        
        if request.id < 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Product ID must be a positive integer.")
            return db_pb2.Product()
        
        conn = None
        try:
            conn = simple_pool.get_conn()
            with conn.cursor() as cursor:
                query = """
                    SELECT id, name, description, category, price, slogan, stock, created_at 
                    FROM products WHERE id = %s;
                """
                cursor.execute(query, (request.id,))

                row = cursor.fetchone()

                if row is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Product with ID {request.id} not found.")
                    return db_pb2.Product()

                product = db_pb2.Product(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    category=row[3],
                    price=float(row[4]),
                    slogan=row[5],
                    stock=row[6]
                )

                if row[7] is not None:
                    ts = Timestamp()
                    ts.FromDatetime(row[7])
                    product.created_at.CopyFrom(ts)
                
                return product
            
        except Exception as e:
            pprint(f"Database error in GetProduct: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {e}")
            return db_pb2.Product()
        
        finally:
            if conn:
                simple_pool.putconn(conn)


    def ListProducts(self, request, context):
        print("Received ListProducts request")

        limit = request.limit if request.limit > 0 else 20
        offset = request.offset if request.offset > 0 else 0

        conn = None
        try: 
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                query = "SELECT id, name, stock, price FROM products ORDER BY id LIMIT %s OFFSET %s;"
                cursor.execute(query, (limit, offset))

                results = cursor.fetchall()
                pprint(results)

                response = db_pb2.ListProductsResponse()
                for row in results:
                    product = response.products.add() # adds a new element at the end
                    product.id = row[0]
                    product.name = row[1]
                    product.stock = row[2]
                    product.price = float(row[3])
                return response
        except Exception as e:
            pprint(f"Database error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {e}")
            return db_pb2.ListProductsResponse() # an empty response
        finally:
            if conn:
                simple_pool.putconn(conn)

    def UpdateProduct(self, request, context):
        print(f"Received UpdateProduct request for ID: {request.id}")

        # server checking
        if request.id < 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Product ID must be provided for an update.")
            return db_pb2.Product()
        if not request.name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Product name is required.")
            return db_pb2.Product()
        if request.price < 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Product price cannot be negative.")
            return db_pb2.Product()
        if request.stock < 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Product stock cannot be negative.")
            return db_pb2.Product()
        
        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                # use UPDATE ... SET ... WHERE ... RETURNING *
                query = """
                    UPDATE products
                    SET name = %s, description = %s, category = %s, price = %s, slogan = %s, stock = %s
                    WHERE id = %s
                    RETURNING id, name, description, category, price, slogan, stock, created_at;
                """
                cursor.execute(query, (
                    request.name,
                    request.description,
                    request.category,
                    request.price,
                    request.slogan,
                    request.stock,
                    request.id  # id 用于 WHERE 子句
                ))

                updated_row = cursor.fetchone()

                if updated_row is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Product with ID {request.id} not found, cannot update.")
                    return db_pb2.Product()
                
                conn.commit()

                product = db_pb2.Product(
                    id=updated_row[0],
                    name=updated_row[1],
                    description=updated_row[2],
                    category=updated_row[3],
                    price=float(updated_row[4]),
                    slogan=updated_row[5],
                    stock=updated_row[6]
                )
                
                if updated_row[7] is not None:
                    ts = Timestamp()
                    ts.FromDatetime(updated_row[7])
                    product.created_at.CopyFrom(ts)
                
                print(f"Successfully updated product with ID: {product.id}")
                return product

        except Exception as e:
            pprint(f"An unexpected error occurred in UpdateProduct: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"An unexpected error occurred: {e}")
            return db_pb2.Product()
        finally:
            if conn:
                simple_pool.putconn(conn)

    def DeleteProduct(self, request, context):
        print(f"Received DeleteProduct request for ID: {request.id}")

        # server check
        if request.id < 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Product ID must be a positive integer.")
            return empty_pb2.Empty()
        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                query = "DELETE FROM products WHERE id = %s;"
                cursor.execute(query, (request.id,))

                # check if the row is deleted
                if cursor.rowcount == 0:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Product with ID {request.id} not found, cannot delete.")
                    return empty_pb2.Empty()

                conn.commit()

                print(f"Successfully deleted product with ID: {request.id}")
                return empty_pb2.Empty()

        except Exception as e:
            pprint(f"An unexpected error occurred in DeleteProduct: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"An unexpected error occurred: {e}")
            return empty_pb2.Empty()
        finally:
            if conn:
                simple_pool.putconn(conn)

class UserServiceServicer(db_pb2_grpc.UserServiceServicer):
    def CreateUser(self, request, context):
        print(f"Received CreateUser request for username: {request.username}")

        # 1. 服务器端校验
        if not all([request.sid, request.username, request.email, request.password_hash]):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("sid, username, email, and password_hash are required.")
            return db_pb2.User()
        
        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                # insert data
                query = """
                    INSERT INTO users (sid, username, email, password_hash)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, sid, username, email, created_at;
                """
                cursor.execute(query, (
                    request.sid,
                    request.username,
                    request.email,
                    request.password_hash
                ))
                new_row = cursor.fetchone()
                conn.commit()

                if new_row is None:
                    raise Exception("Failed to retrieve the new user after insertion.")

                # return message, password not included
                user = db_pb2.User(
                    id=new_row[0],
                    sid=new_row[1],
                    username=new_row[2],
                    email=new_row[3]
                )
                if new_row[4] is not None:
                    ts = Timestamp()
                    ts.FromDatetime(new_row[4])
                    user.created_at.CopyFrom(ts)
                
                print(f"Successfully created user with ID: {user.id}")
                return user
        except psycopg2.Error as e:
            if e.pgcode == '23505': # unique_violation
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(f"User with conflicting sid, username, or email already exists. Details: {e.diag.constraint_name}")
            else:
                pprint(f"Database error in CreateUser: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal server error: {e}")
            return db_pb2.User()
        finally:
            if conn:
                simple_pool.putconn(conn)

    def GetUser(self, request, context):
        print(f"Received GetUser request for ID: {request.id}")
        if request.id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("User ID must be a positive integer.")
            return db_pb2.User()

        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                # no password_hash
                query = "SELECT id, sid, username, email, created_at FROM users WHERE id = %s;"
                cursor.execute(query, (request.id,))
                row = cursor.fetchone()

                if row is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"User with ID {request.id} not found.")
                    return db_pb2.User()

                user = db_pb2.User(id=row[0], sid=row[1], username=row[2], email=row[3])
                if row[4] is not None:
                    ts = Timestamp()
                    ts.FromDatetime(row[4])
                    user.created_at.CopyFrom(ts)
                return user
        except Exception as e:
            pprint(f"Database error in GetUser: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {e}")
            return db_pb2.User()
        finally:
            if conn:
                simple_pool.putconn(conn)

    def ListUsers(self, request, context):
        print(f"Received ListUsers request with limit={request.limit}, offset={request.offset}")
        limit = request.limit if request.limit > 0 else 20
        offset = request.offset if request.offset >= 0 else 0

        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                query = "SELECT id, sid, username, email, created_at FROM users ORDER BY id LIMIT %s OFFSET %s;"
                cursor.execute(query, (limit, offset))
                results = cursor.fetchall()

                response = db_pb2.ListUsersResponse()
                for row in results:
                    user = response.users.add()
                    user.id = row[0]
                    user.sid = row[1]
                    user.username = row[2]
                    user.email = row[3]
                    if row[4] is not None:
                        ts = Timestamp()
                        ts.FromDatetime(row[4])
                        user.created_at.CopyFrom(ts)
                return response
        except Exception as e:
            pprint(f"Database error in ListUsers: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {e}")
            return db_pb2.ListUsersResponse()
        finally:
            if conn:
                simple_pool.putconn(conn)

    def UpdateUser(self, request, context):
        print(f"Received UpdateUser request for ID: {request.id}")
        if request.id < 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("User ID must be provided for an update.")
            return db_pb2.User()
        
        updates = [] # choose what to update
        params = []
        if request.email:
            updates.append("email = %s")
            params.append(request.email)
        if request.password_hash:
            updates.append("password_hash = %s")
            params.append(request.password_hash)

        if not updates:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("No fields to update were provided (email or password_hash).")
            return db_pb2.User()

        params.append(request.id) 
        set_clause = ", ".join(updates)

        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                query = f"UPDATE users SET {set_clause} WHERE id = %s RETURNING id, sid, username, email, created_at;"
                cursor.execute(query, tuple(params))
                updated_row = cursor.fetchone()

                if updated_row is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"User with ID {request.id} not found, cannot update.")
                    return db_pb2.User()
                
                conn.commit()
                user = db_pb2.User(id=updated_row[0], sid=updated_row[1], username=updated_row[2], email=updated_row[3])
                if updated_row[4] is not None:
                    ts = Timestamp()
                    ts.FromDatetime(updated_row[4])
                    user.created_at.CopyFrom(ts)
                return user
        except psycopg2.Error as e:
            if e.pgcode == '23505':
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(f"Update failed: email '{request.email}' may already be in use.")
            else:
                pprint(f"Database error in UpdateUser: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal server error: {e}")
            return db_pb2.User()
        finally:
            if conn:
                simple_pool.putconn(conn)

    def DeleteUser(self, request, context):
        print(f"Received DeleteUser request for ID: {request.id}")
        if request.id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("User ID must be a positive integer.")
            return empty_pb2.Empty()

        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s;", (request.id,))
                if cursor.rowcount == 0:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"User with ID {request.id} not found, cannot delete.")
                    return empty_pb2.Empty()
                conn.commit()
                print(f"Successfully deleted user with ID: {request.id}")
                return empty_pb2.Empty()
        except Exception as e:
            pprint(f"An unexpected error occurred in DeleteUser: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"An unexpected error occurred: {e}")
            return empty_pb2.Empty()
        finally:
            if conn:
                simple_pool.putconn(conn)

class OrderServiceServicer(db_pb2_grpc.OrderServiceServicer):
    def CreateOrder(self, request, context):
        print(f"Received CreateOrder request for user_id: {request.user_id}")

        # check
        if not all([request.user_id > 0, request.product_id > 0, request.quantity > 0, request.total_price >= 0]):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("user_id, product_id, and quantity must be positive, and total_price must be non-negative.")
            return db_pb2.Order()

        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                # update stock information
                cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s;", 
                               (request.quantity, request.product_id, request.quantity))
                if cursor.rowcount == 0:
                    raise Exception("Insufficient stock or product not found.")

                # insert order
                query = """
                    INSERT INTO orders (user_id, product_id, quantity, total_price)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, user_id, product_id, quantity, total_price, created_at;
                """
                cursor.execute(query, (
                    request.user_id,
                    request.product_id,
                    request.quantity,
                    request.total_price
                ))
                new_row = cursor.fetchone()
                conn.commit()

                if new_row is None:
                    raise Exception("Failed to retrieve the new order after insertion.")
                
                order = db_pb2.Order(
                    id=new_row[0],
                    user_id=new_row[1],
                    product_id=new_row[2],
                    quantity=new_row[3],
                    total_price=float(new_row[4])
                )
                if new_row[5] is not None:
                    ts = Timestamp()
                    ts.FromDatetime(new_row[5])
                    order.created_at.CopyFrom(ts)
                
                print(f"Successfully created order with ID: {order.id}")
                return order
        except psycopg2.Error as e:
            if e.pgcode == '23503': # foreign_key_violation
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Referenced user or product not found. Details: {e.diag.constraint_name}")
            else:
                pprint(f"Database error in CreateOrder: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal server error: {e}")
            return db_pb2.Order()
        finally:
            if conn:
                simple_pool.putconn(conn)

    def GetOrder(self, request, context):
        print(f"Received GetOrder request for ID: {request.id}")
        if request.id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Order ID must be a positive integer.")
            return db_pb2.Order()

        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                query = "SELECT id, user_id, product_id, quantity, total_price, created_at FROM orders WHERE id = %s;"
                cursor.execute(query, (request.id,))
                row = cursor.fetchone()

                if row is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Order with ID {request.id} not found.")
                    return db_pb2.Order()

                order = db_pb2.Order(id=row[0], user_id=row[1], product_id=row[2], quantity=row[3], total_price=float(row[4]))
                if row[5] is not None:
                    ts = Timestamp()
                    ts.FromDatetime(row[5])
                    order.created_at.CopyFrom(ts)
                return order
        except Exception as e:
            pprint(f"Database error in GetOrder: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {e}")
            return db_pb2.Order()
        finally:
            if conn:
                simple_pool.putconn(conn)

    def ListOrdersByUser(self, request, context):
        print(f"Received ListOrdersByUser request for user_id: {request.user_id}")
        if request.user_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("User ID must be a positive integer.")
            return db_pb2.ListOrdersResponse()

        limit = request.limit if request.limit > 0 else 20
        offset = request.offset if request.offset >= 0 else 0

        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                query = "SELECT id, user_id, product_id, quantity, total_price, created_at FROM orders WHERE user_id = %s ORDER BY id DESC LIMIT %s OFFSET %s;"
                cursor.execute(query, (request.user_id, limit, offset))
                results = cursor.fetchall()

                response = db_pb2.ListOrdersResponse()
                for row in results:
                    order = response.orders.add()
                    order.id = row[0]
                    order.user_id = row[1]
                    order.product_id = row[2]
                    order.quantity = row[3]
                    order.total_price = float(row[4])
                    if row[5] is not None:
                        ts = Timestamp()
                        ts.FromDatetime(row[5])
                        order.created_at.CopyFrom(ts)
                return response
        except Exception as e:
            pprint(f"Database error in ListOrdersByUser: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {e}")
            return db_pb2.ListOrdersResponse()
        finally:
            if conn:
                simple_pool.putconn(conn)
    
    def DeleteOrder(self, request, context):
        print(f"Received DeleteOrder request for ID: {request.id}")
        if request.id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Order ID must be a positive integer.")
            return empty_pb2.Empty()

        conn = None
        try:
            conn = simple_pool.getconn()
            with conn.cursor() as cursor:
                # recover stock
                cursor.execute("UPDATE products SET stock = stock + (SELECT quantity FROM orders WHERE id = %s) WHERE id = (SELECT product_id FROM orders WHERE id = %s);",
                               (request.id, request.id))

                cursor.execute("DELETE FROM orders WHERE id = %s;", (request.id,))
                if cursor.rowcount == 0:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Order with ID {request.id} not found, cannot delete.")
                    return empty_pb2.Empty()
                
                conn.commit()
                print(f"Successfully deleted order with ID: {request.id}")
                return empty_pb2.Empty()
        except Exception as e:
            pprint(f"An unexpected error occurred in DeleteOrder: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"An unexpected error occurred: {e}")
            return empty_pb2.Empty()
        finally:
            if conn:
                simple_pool.putconn(conn)


def serve():
    # create a gRPC server instance with threadpool
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # add services to the server
    db_pb2_grpc.add_ProductServiceServicer_to_server(ProductServiceServicer(), server)
    db_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    db_pb2_grpc.add_OrderServiceServicer_to_server(OrderServiceServicer(), server)

    # server listens at 50051 port
    port = '50051'
    server.add_insecure_port(f'[::]:{port}')
    
    # start the server
    server.start() # non-blocking
    print(f"gRPC server started, listening on port {port}...")

    # keep main thread running 
    try:
        while True:
            time.sleep(86400)  # avoid main thread existing
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop(0) 


if __name__ == '__main__':
    serve()