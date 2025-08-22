# Python 类型提示（Type Hints）完全指南

Python 3.5 引入了类型提示（Type Hints）功能，这是一种可选的静态类型标注方式，可以帮助开发者编写更清晰、更健壮的代码。本指南将全面介绍 Python 类型提示的使用方法、最佳实践和高级技巧。

## 目录

1. [基础知识](#基础知识)
2. [基本类型](#基本类型)
3. [复合类型](#复合类型)
4. [函数类型提示](#函数类型提示)
5. [类和自定义类型](#类和自定义类型)
6. [泛型](#泛型)
7. [类型别名](#类型别名)
8. [Union 和 Optional 类型](#union-和-optional-类型)
9. [Callable 类型](#callable-类型)
10. [Protocol 和结构化类型](#protocol-和结构化类型)
11. [TypedDict](#typeddict)
12. [Literal 类型](#literal-类型)
13. [Final 和常量](#final-和常量)
14. [类型检查工具](#类型检查工具)
15. [最佳实践](#最佳实践)
16. [常见问题解答](#常见问题解答)

## 基础知识

类型提示是 Python 的一个可选功能，它不会影响代码的运行时行为，但可以：

- 提高代码可读性
- 帮助 IDE 提供更好的代码补全和错误检查
- 与静态类型检查工具（如 mypy）配合使用，在运行前发现潜在错误
- 作为代码文档的一部分

要使用类型提示，需要导入 `typing` 模块：

```python
from typing import List, Dict, Tuple, Set, Optional, Union, Any
```

Python 3.9+ 简化了一些常见类型的导入，可以直接使用内置类型作为泛型：

```python
# Python 3.9+
list[int]       # 替代 List[int]
dict[str, int]  # 替代 Dict[str, int]
tuple[int, str] # 替代 Tuple[int, str]
```

## 基本类型

为变量添加类型提示：

```python
age: int = 25
name: str = "Alice"
height: float = 1.75
is_student: bool = True
```

## 复合类型

### 列表、字典、元组和集合

```python
from typing import List, Dict, Tuple, Set

# 列表
numbers: List[int] = [1, 2, 3, 4]
names: List[str] = ["Alice", "Bob", "Charlie"]

# Python 3.9+
numbers: list[int] = [1, 2, 3, 4]

# 字典
user_ages: Dict[str, int] = {"Alice": 25, "Bob": 30}
# Python 3.9+
user_ages: dict[str, int] = {"Alice": 25, "Bob": 30}

# 元组
point: Tuple[int, int] = (10, 20)  # 固定长度，不同类型
coordinates: Tuple[float, ...] = (1.0, 2.0, 3.0)  # 可变长度，相同类型
# Python 3.9+
point: tuple[int, int] = (10, 20)

# 集合
unique_numbers: Set[int] = {1, 2, 3}
# Python 3.9+
unique_numbers: set[int] = {1, 2, 3}
```

## 函数类型提示

为函数参数和返回值添加类型提示：

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add_numbers(a: int, b: int) -> int:
    return a + b

def process_items(items: List[str]) -> None:
    for item in items:
        print(item)
```

## 类和自定义类型

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name: str = name
        self.age: int = age

    def get_profile(self) -> str:
        return f"{self.name}, {self.age} years old"

def create_user(name: str, age: int) -> User:
    return User(name, age)
```

## 泛型

创建泛型函数和类：

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')  # 定义类型变量

def first_element(items: List[T]) -> T:
    return items[0]

# 使用
number = first_element([1, 2, 3])  # 类型推断为 int
name = first_element(["Alice", "Bob"])  # 类型推断为 str

# 泛型类
class Box(Generic[T]):
    def __init__(self, content: T) -> None:
        self.content: T = content
    
    def get_content(self) -> T:
        return self.content

int_box = Box[int](123)
str_box = Box[str]("Hello")
```

## 类型别名

创建类型别名以简化复杂类型：

```python
from typing import Dict, List, Tuple

# 定义类型别名
UserId = int
UserName = str
UserInfo = Dict[str, str]
Point = Tuple[float, float]
Points = List[Point]

# 使用类型别名
def get_user(user_id: UserId) -> UserInfo:
    # ...
    return {"name": "Alice", "email": "alice@example.com"}

def calculate_distance(points: Points) -> float:
    # ...
    return 10.5
```

## Union 和 Optional 类型

表示多种可能的类型：

```python
from typing import Union, Optional

# Union 表示多种可能的类型
def process_data(data: Union[str, int, float]) -> str:
    return str(data)

# Optional 等价于 Union[T, None]
def get_user_name(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None

# Python 3.10+ 可以使用 | 操作符
def process_input(data: str | int | float) -> str:  # Python 3.10+
    return str(data)
```

## Callable 类型

表示可调用对象（函数、方法等）：

```python
from typing import Callable

# 接受一个函数作为参数，该函数接受 int 并返回 str
def apply_formatter(value: int, formatter: Callable[[int], str]) -> str:
    return formatter(value)

# 使用示例
def format_as_currency(amount: int) -> str:
    return f"${amount:.2f}"

result = apply_formatter(100, format_as_currency)  # "$100.00"
```

## Protocol 和结构化类型

使用 Protocol 实现结构化类型（鸭子类型）：

```python
from typing import Protocol, List

# 定义协议
class Drawable(Protocol):
    def draw(self) -> None: ...

# 实现协议的类（无需显式继承）
class Circle:
    def draw(self) -> None:
        print("Drawing a circle")

class Square:
    def draw(self) -> None:
        print("Drawing a square")

# 使用协议作为类型提示
def render(drawable: Drawable) -> None:
    drawable.draw()

# 使用
render(Circle())  # 有效
render(Square())  # 有效
```

## TypedDict

为字典提供结构化类型提示：

```python
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: str

# 创建符合 TypedDict 的字典
user: UserDict = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
}

# 可选字段
class MovieDict(TypedDict, total=False):
    title: str  # 必需字段
    year: int   # 可选字段
    director: str  # 可选字段

movie: MovieDict = {"title": "Inception"}  # 有效
```

## Literal 类型

限制变量只能是特定的字面值：

```python
from typing import Literal

# 限制参数只能是特定的字符串值
def move(direction: Literal["up", "down", "left", "right"]) -> None:
    print(f"Moving {direction}")

move("up")      # 有效
move("forward")  # 类型检查器会报错
```

## Final 和常量

标记不应被修改的变量：

```python
from typing import Final

MAX_SPEED: Final = 120
CONFIG: Final[Dict[str, str]] = {"host": "localhost", "port": "8080"}

# 尝试修改会被类型检查器标记为错误
MAX_SPEED = 150  # 错误
```

## 类型检查工具

### mypy

mypy 是最流行的 Python 静态类型检查工具：

```bash
# 安装
pip install mypy

# 使用
mypy your_script.py
```

### 其他类型检查工具

- pyright/Pylance (Microsoft)
- Pytype (Google)
- Pyre (Facebook)

## 最佳实践

1. **逐步添加类型提示**：不需要一次性为所有代码添加类型提示，可以从关键模块开始。

2. **使用类型注释而非注释**：使用类型提示代替注释来说明参数和返回值类型。

3. **为公共 API 添加类型提示**：优先为库的公共接口添加类型提示。

4. **使用 `Any` 类型谨慎**：`Any` 类型会绕过类型检查，应尽量避免使用。

5. **利用类型推断**：Python 类型检查器可以推断许多类型，不必处处添加类型提示。

6. **使用 `reveal_type()`**：在 mypy 中使用 `reveal_type(variable)` 来查看变量的推断类型。

7. **考虑兼容性**：如果需要支持旧版本 Python，可以使用注释形式的类型提示：

   ```python
   def greet(name):  # type: (str) -> str
       return f"Hello, {name}!"
   ```

## 常见问题解答

### 类型提示会影响性能吗？

不会。类型提示在运行时基本被忽略，不会影响代码执行性能。

### 如何处理循环导入问题？

使用字符串字面值作为类型提示：

```python
class Node:
    def __init__(self) -> None:
        self.children: List["Node"] = []  # 使用字符串字面值
```

或使用 `if TYPE_CHECKING`：

```python
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from other_module import SomeClass

def process(data: "SomeClass") -> None:
    pass
```

### 如何为动态属性添加类型提示？

使用 `__annotations__` 字典：

```python
class DynamicClass:
    def __init__(self) -> None:
        self.__annotations__ = {"dynamic_attr": str}
        self.dynamic_attr = "value"
```

### 如何处理第三方库没有类型提示的情况？

可以使用存根文件（stub files）或安装类型存根包：

```bash
pip install types-requests  # 为 requests 库安装类型存根
```

---

通过本指南，你应该能够开始在 Python 项目中有效地使用类型提示，提高代码质量和可维护性。随着你对类型系统的深入了解，你会发现它是一个强大的工具，可以帮助你编写更健壮、更易于理解的代码。