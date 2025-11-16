# 创建 __init__.py 文件，确保 'gen' 是一个包
touch db_proto/__init__.py

# 运行 protoc 命令
# 关键：-I=. 和 --python_out=. 让 protoc 镜像输入路径来创建输出
python -m grpc_tools.protoc \
    -I=. \
    --python_out=. \
    --grpc_python_out=. \
    --pyi_out=. \
    db_proto/db.proto

echo "gRPC code generated successfully inside the 'db_proto/' package."