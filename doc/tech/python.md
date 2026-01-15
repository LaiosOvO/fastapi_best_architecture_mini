# Python 基础语法指南

## 1. 变量和数据类型

### 1.1 基本数据类型
```python
# 整数
age = 25

# 浮点数
price = 19.99

# 字符串
name = "张三"
message = 'Hello World'

# 布尔值
is_active = True
is_deleted = False

# 空值
empty_value = None
```

### 1.2 复合数据类型
```python
# 列表 (List) - 有序可变
fruits = ['apple', 'banana', 'orange']
numbers = [1, 2, 3, 4, 5]

# 元组 (Tuple) - 有序不可变
coordinates = (10, 20)
rgb_color = (255, 0, 0)

# 字典 (Dictionary) - 键值对
person = {
    'name': '李四',
    'age': 30,
    'city': '北京'
}

# 集合 (Set) - 无序不重复
unique_numbers = {1, 2, 3, 4, 5}
```

## 2. 控制流

### 2.1 条件语句
```python
age = 18

if age >= 18:
    print("成年人")
elif age >= 13:
    print("青少年")
else:
    print("儿童")
```

### 2.2 循环语句
```python
# for 循环
for i in range(5):
    print(i)

# 遍历列表
fruits = ['apple', 'banana', 'orange']
for fruit in fruits:
    print(fruit)

# while 循环
count = 0
while count < 5:
    print(count)
    count += 1
```

## 3. 函数

### 3.1 基本函数定义
```python
def greet(name):
    return f"Hello, {name}!"

# 调用函数
message = greet("Alice")
print(message)  # 输出: Hello, Alice!
```

### 3.2 带默认参数的函数
```python
def create_user(name, age=18, city="未知"):
    return {
        'name': name,
        'age': age,
        'city': city
    }

user = create_user("张三")
print(user)  # {'name': '张三', 'age': 18, 'city': '未知'}
```

### 3.3 可变参数
```python
def sum_all(*args):
    """接受任意数量的位置参数"""
    return sum(args)

def print_info(**kwargs):
    """接受任意数量的关键字参数"""
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print(sum_all(1, 2, 3, 4, 5))  # 15
print_info(name="李四", age=25)  # name: 李四, age: 25
```

## 4. 类和对象

### 4.1 基本类定义
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"你好，我是 {self.name}"
    
    def is_adult(self):
        return self.age >= 18

# 创建对象
person = Person("王五", 25)
print(person.greet())  # 你好，我是 王五
print(person.is_adult())  # True
```

### 4.2 继承
```python
class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)
        self.student_id = student_id
    
    def study(self):
        return f"{self.name} 正在学习"

student = Student("小明", 20, "S001")
print(student.greet())  # 你好，我是 小明
print(student.study())  # 小明 正在学习
```

## 5. 异常处理

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    print("无论是否有异常都会执行")
```

## 6. 文件操作

```python
# 写入文件
with open('example.txt', 'w', encoding='utf-8') as f:
    f.write('Hello, World!')

# 读取文件
with open('example.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)  # Hello, World!
```

## 7. 模块和包

### 7.1 导入模块
```python
import math
import os
from datetime import datetime
from random import randint

# 使用导入的模块
area = math.pi * 5 ** 2
current_time = datetime.now()
random_num = randint(1, 100)
```

### 7.2 创建模块
```python
# my_module.py
def hello():
    return "Hello from my module!"

PI = 3.14159
```

```python
# 使用自定义模块
import my_module

print(my_module.hello())  # Hello from my module!
print(my_module.PI)       # 3.14159
```

## 8. 装饰器

```python
def timer(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行时间: {end - start:.2f}秒")
        return result
    return wrapper

@timer
def slow_function():
    import time
    time.sleep(1)
    return "完成"

slow_function()  # slow_function 执行时间: 1.00秒
```

## 9. 生成器和迭代器

```python
# 生成器函数
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# 使用生成器
for num in fibonacci(10):
    print(num)  # 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
```

## 10. 异步编程

```python
import asyncio

async def fetch_data():
    print("开始获取数据...")
    await asyncio.sleep(1)  # 模拟异步操作
    print("数据获取完成")
    return "数据"

async def main():
    result = await fetch_data()
    print(result)

# 运行异步函数
asyncio.run(main())
```

## 11. 类型注解 (Type Hints)

```python
from typing import List, Dict, Optional, Union

def process_numbers(numbers: List[int]) -> int:
    return sum(numbers)

def get_user_info(user_id: int) -> Optional[Dict[str, Union[str, int]]]:
    if user_id == 1:
        return {"name": "张三", "age": 25}
    return None

# 使用类型注解的函数
result = process_numbers([1, 2, 3, 4, 5])  # 返回 15
user = get_user_info(1)  # 返回字典或 None
```

## 12. 数据类 (Data Classes)

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    
    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

point = Point(3.0, 4.0)
print(point.distance_from_origin())  # 5.0
```

## 13. 上下文管理器

```python
class DatabaseConnection:
    def __enter__(self):
        print("连接数据库")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("断开数据库连接")
    
    def query(self, sql):
        return f"执行查询: {sql}"

# 使用上下文管理器
with DatabaseConnection() as db:
    result = db.query("SELECT * FROM users")
    print(result)
# 自动执行 __exit__ 方法
```

## 14. 常用内置函数

```python
# map - 对序列中每个元素应用函数
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))  # [1, 4, 9, 16, 25]

# filter - 过滤序列
evens = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]

# zip - 将多个序列打包
names = ['Alice', 'Bob', 'Charlie']
ages = [25, 30, 35]
combined = list(zip(names, ages))  # [('Alice', 25), ('Bob', 30), ('Charlie', 35)]

# enumerate - 同时获取索引和值
for index, value in enumerate(['a', 'b', 'c']):
    print(f"{index}: {value}")
```

## 15. 列表推导式

```python
# 基本列表推导式
squares = [x**2 for x in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 带条件的列表推导式
even_squares = [x**2 for x in range(10) if x % 2 == 0]
print(even_squares)  # [0, 4, 16, 36, 64]

# 字典推导式
word_lengths = {word: len(word) for word in ['hello', 'world', 'python']}
print(word_lengths)  # {'hello': 5, 'world': 5, 'python': 6}
```

这份文档涵盖了 Python 的核心语法和常用特性，为学习 FastAPI 奠定了坚实的基础。