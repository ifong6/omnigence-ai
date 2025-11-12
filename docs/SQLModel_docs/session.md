# 🧠 SQLModel Session 概览

## 🎯 什么是 Session？

在 SQLModel（基于 SQLAlchemy）中，**Session 是 ORM 模型与数据库交互的核心接口**。它负责管理数据库连接、事务，以及 ORM 对象的生命周期。

一句话总结：

> `Session` 是数据库的 **上下文管理器**，掌控着 **连接、事务、对象状态**。

---

## ⚙️ Session 的三大主要目的

### 1️⃣ 数据库连接与事务管理

* `Session` 管理数据库连接的整个生命周期。
* 它自动处理事务的开启、提交、回滚与关闭。
* 使用 `with Session(engine) as session:` 语法可以确保资源自动清理。

```python
with Session(engine) as session:
    repo = CompanyRepo(session)
    company = repo.create(name="Example Co.")
    session.commit()  # ✅ 提交事务，写入数据库
```

**要点：**

* 不调用 `commit()`，更改不会真正写入数据库。
* 出现异常时会自动回滚。
* 离开 `with` 块时自动关闭连接。

---

### 2️⃣ 对象追踪与状态管理

* `Session` 会追踪所有被加载或新建的 ORM 对象。
* 当你修改这些对象的属性时，ORM 会在 `flush()` 或 `commit()` 时自动生成对应的 SQL 语句。

```python
company = session.get(Company, 1)
company.address = "新地址"
session.commit()  # ✅ 自动生成 UPDATE 语句
```

**好处：**

* 不需要手写 `UPDATE` 或 `INSERT` 语句。
* 保证数据一致性（同一个对象在同一个事务中只有一个实例）。
* 支持自动 `flush()`，在提交前同步未保存的更改。

---

### 3️⃣ ORM 查询与结果管理

* 所有 ORM 查询都在 `Session` 环境中执行。
* 它提供统一的接口来执行、过滤和删除 ORM 对象。

```python
results = session.exec(select(Company).where(Company.name == "ACME"))
for company in results:
    print(company.name)
```

**常用操作：**

* `exec()`：执行 ORM 查询。
* `get()`：根据主键获取记录。
* `delete()`：删除对象。
* `refresh()`：刷新对象以获取最新数据库状态。

关闭 Session 后，对象将变为 **“脱离状态（detached）”**，此时无法再修改或刷新。

---

## 🧾 总结表格

| 目的          | 描述              | 常用方法                                |
| ----------- | --------------- | ----------------------------------- |
| 1️⃣ 连接与事务管理 | 负责数据库连接与事务生命周期  | `commit()`, `rollback()`, `close()` |
| 2️⃣ 对象追踪    | 追踪对象状态并自动生成 SQL | `add()`, `flush()`, `refresh()`     |
| 3️⃣ 查询与结果管理 | 执行 ORM 查询与结果处理  | `exec()`, `get()`, `delete()`       |

---

## ✅ 最佳实践总结

* 使用上下文管理器（`with Session(engine) as session:`）以确保安全。
* 写操作后务必调用 `session.commit()`。
* 每个逻辑单元（如一次 Web 请求或工作流）只使用一个 Session。
* 保持 Session 生命周期短，防止连接过期或数据不一致。

---

### ✨ 一句话总结

> **SQLModel 的 Session 就是你的数据库上下文管理器——它负责管理连接、事务以及对象状态，确保 ORM 操作安全而优雅。**
