import grpc
from db_proto.db_pb2 import ListProductsRequest
from db_proto.db_pb2_grpc import ProductServiceStub


def run():
  with grpc.insecure_channel('localhost:50051') as channel:
    stub = ProductServiceStub(channel)
    # list products
    print('--- Calling ListProducts ---')
    request = ListProductsRequest(limit=10, offset=0)
    response = stub.ListProducts(request)

    if not response.products:
        print("No products found in the database.")
    else:
        print(f"Received {len(response.products)} products:")
        for product in response.products:
            print("--------------------")
            print(f"  ID:          {product.id}")
            print(f"  Name:        {product.name}")
            print(f"  Category:    {product.category}")
            print(f"  Price:       {product.price:.2f}") # 格式化为两位小数
            print(f"  Stock:       {product.stock}")
            print(f"  Slogan:      {product.slogan}")


if __name__ == '__main__':
  run()
