# Repository Layer Design Guide（通用 Repo 设计）

> 面向应用的持久化访问层抽象：隔离业务逻辑与数据库、提升可测试性与可维护性。

## 🎯 目标

* **隔离**：让业务层（Service/Use Case）不关心 SQL/连接/驱动细节。
* **类型安全**：输入/输出统一由 Pydantic/SQLModel 模型约束。
* **可测试**：可替换/Mock Repo，单测不用连真库。
* **可演进**：数据库变更（表名/列名/索引）尽量不波及业务层。

## 🧱 分层职责

* **Model 层**：定义 Table 模型（`TableModel`）、输入模型（`CreateModel`/`UpdateModel`）、输出模型（`ReadModel`/`RowModel`）。
* **Repo 基类**：封装通用 CRUD（`insert/update_where/find_xxx/execute_raw`）、表名/白名单列校验、参数化执行。
* **具体 Repo**：组织面向业务的查询方法（按 id、按外键、搜索、分页等），并承担**模型之间的转换**（`Create/Update` ⇄ `Row`）。

## 🧩 模型拆分建议

* `TableModel`：真实表结构（含 DB 默认值/约束）。
* `CreateModel`：创建时允许字段更宽松（主键可选、部分字段可空）。
* `UpdateModel`：全部字段可选（便于局部更新）。
* `ReadModel`（或 `RowModel`）：读取返回（可含 `created_at/updated_at` 等只读列）。

> 这样可以避免“写入/读取/表结构”三者在一个模型里相互牵制。

## 🔑 UUID 与序列化

* **输入（Create/Update）**：接受 `UUID` 或字符串，统一在 Repo 内部转换为 DB 期望格式（常见是 `str(UUID)`）。
* **输出（Read）**：保持为 `UUID`（便于上层继续强类型使用）。
* 若驱动天然支持 `uuid.UUID`，可免去转换；若遇到 `can't adapt type 'UUID'`，在 Repo 层集中做 `UUID → str`。

## 🔒 安全与健壮性

* 一律使用**参数化查询**，避免 SQL 注入。
* 表名/列名只从**白名单**选择（`allowed_cols`），不要直接拼接用户输入。
* 对 `limit/offset/order_by` 做白名单或校验。
* 统一错误包装为**业务可读异常**（并记录底层异常）。

## 📈 分页与排序

* 统一方法签名：`list_xxx(limit, offset, order_by)`；默认使用**时间列**（`created_at DESC`）而不是主键或随机 UUID。
* 结果同时返回 `items + next_cursor`（如需游标分页）。

## 🧪 测试策略

* 基类用假连接/内存桩替换，验证 SQL 组装与参数绑定。
* 每个 Repo 的复杂查询各写 1–2 个单测：输入 → 期望 SQL/参数 → 桩返回 → 最终 `RowModel`。

## 🧰 日志与可观测

* 在 Repo 基类拦截执行：记录**表名/操作/耗时/影响行数**，适当打印 SQL 模板与参数（脱敏）。

## ✅ 最小示例（片段）

```python
class BaseRepository:
    def __init__(self, table: str, allowed_cols: set[str]): ...
    def insert(self, data: dict) -> dict: ...
    def update_where(self, data: dict, where_sql: str, params: tuple) -> list[dict]: ...
    def find_one_by(self, col: str, value) -> dict | None: ...
    def find_many_by(self, col: str, value, *, order_by: str, limit: int | None) -> list[dict]: ...
    def execute_raw(self, sql: str, params: tuple | None = None) -> list[dict]: ...
```

## 📝 代码风格清单

* `model_dump(exclude_none=True)`（Pydantic v2）/ `dict(exclude_none=True)`（v1）
* 将 UUID 统一转换放在**一个小工具**或 Repo 内部 `_normalize()`。
* `ReadModel(**row)` 前先做**键存在性**或**默认值**处理。
* 返回列表用列表推导统一 `RowModel(**row)`。

---

