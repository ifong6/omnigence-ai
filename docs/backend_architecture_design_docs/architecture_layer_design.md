# Layered Architecture Design — Controller / Service / DAO / Database

## 以现实生活比喻理解架构

**Controller（客服）** → **Service（经理）** → **DAO（仓库管理员）** → **Database（仓库）**

---

## 1️⃣ 整体概念

系统每一层都有明确职责，唔可以"跨层干活"：

| 层级 | 角色比喻 | 主要职责 | 是否接触数据库 |
|------|----------|----------|----------------|
| Controller (Agent) | 客服 | 接收客户请求，提供服务结果 | ❌ 否 |
| Service | 经理 | 处理业务逻辑、做决策、协调多个仓库 | ⚠️ 间接 |
| DAO (Repository) | 仓库管理员 | 负责实际查数、存数 | ✅ 是 |
| Database | 仓库 | 存储所有数据 | ✅ 是 |

---

## 2️⃣ 数据流与职责说明

```
用户请求（HTTP / Chat / CLI）
   ↓
Controller（客服）
   - 把请求内容封装成 Input DTO
   - 做权限、参数验证
   - 调用 Service
   ↓
Service（经理）
   - 执行业务逻辑
   - 管理事务（commit / rollback）
   - 调用 DAO 拿数据
   ↓
DAO（仓库管理员）
   - 用 ORM / SQL 操作数据库
   - 返回 ORM 对象
   ↓
Database（仓库）
   - 真正存取数据
```

**反方向：**
```
Database → DAO → Service → Controller → 用户响应(JSON)
```

---

## 3️⃣ 各层职责详解

### 🧾 Controller（客服）

只负责接单和派单：

- 接收用户请求（如 HTTP Request）
- 调用对应 Service 方法
- 返回统一响应（DTO → JSON）
- **不做业务逻辑、不动数据库**

**示例代码：**
```python
@router.post("/jobs", response_model=JobDTO)
def create_job(payload: JobCreateDTO, session: Session = Depends(get_session)):
    service = JobService(session)
    return service.create_job(payload)
```

---

### 🧠 Service（经理）

负责任务分配与决策：

- 定义事务边界
- 校验业务规则
- 调用 DAO 获取 / 写入数据
- 统一处理异常与事务回滚
- 输出 DTO（返回给 Controller）
- **不写 SQL，不直接操作 ORM**

**示例代码：**
```python
class JobService:
    def __init__(self, session: Session):
        self.repo = JobDAO(session)
        self.session = session

    def create_job(self, dto: JobCreateDTO) -> JobDTO:
        existing = self.repo.find_by_title(dto.title)
        if existing:
            raise BusinessError("Job title already exists")

        job = Job(title=dto.title, company_id=dto.company_id)
        self.repo.add(job)
        self.session.commit()
        self.session.refresh(job)
        return to_dto(job)
```

---

### 🧱 DAO / Repository（仓库管理员）

负责执行数据库操作：

- 查询（select）、插入（insert）、更新（update）、删除（delete）
- 用 ORM / SQL 执行
- 不处理业务逻辑
- 不控制事务
- **Controller / Service 永远唔直接访问数据库，只通过 DAO**

**示例代码：**
```python
class JobDAO:
    def __init__(self, session: Session):
        self.session = session

    def find_by_title(self, title: str) -> Job | None:
        return self.session.exec(select(Job).where(Job.title == title)).first()

    def add(self, job: Job):
        self.session.add(job)
        return job
```

---

### 🗄️ Database（仓库）

- 数据最终存放处
- 唔理逻辑，只管存储与一致性
- 由 ORM / SQL 进行访问
- 常见选项：PostgreSQL / MySQL / SQLite / MongoDB 等

---

## 4️⃣ 数据与对象边界

| 层级 | 输入 | 输出 | 数据对象 |
|------|------|------|----------|
| Controller | HTTP Request | JSON Response | DTO（Pydantic） |
| Service | Input DTO | Output DTO | DTO + ORM（只在内部转换） |
| DAO | 查询条件 / ORM | ORM 实体 | ORM（SQLModel / SQLAlchemy） |
| Database | SQL 语句 | 结果集 | 表 / 行数据 |

---

## 5️⃣ 现实比喻版（好记易懂）

| 角色 | 中文说明 | 对应层 |
|------|----------|--------|
| 🧍 客服小姐姐 | 接收客户请求，帮客户下单 | Controller |
| 👨‍💼 经理 | 决定订单如何处理，协调多个仓库 | Service |
| 👷 仓库管理员 | 负责搬货、查库存、录入系统 | DAO |
| 🏭 仓库 | 存储货物（数据） | Database |

### 📦 流程：

1. **客户 → 客服 → 经理 → 仓库管理员 → 仓库**
2. **仓库管理员从仓库取货 → 经理确认 → 客服打包 → 客户签收**

---

## 6️⃣ 异常与事务流转

| 层 | 错误类型 | 处理方式 |
|----|----------|----------|
| DAO | 数据层错误（约束、连接、超时） | 抛出 PersistenceError |
| Service | 业务逻辑错误 | 捕获 DAO 错误并封装为 BusinessError |
| Controller | HTTP 层 | 将 BusinessError 映射成 400 / 404 / 422 |

**示例代码：**
```python
try:
    return service.create_job(payload)
except BusinessError as e:
    raise HTTPException(status_code=422, detail=str(e))
```

---

## 7️⃣ 为什么要分三层？

| 目的 | 说明 |
|------|------|
| 安全性 | 用户层永远接触不到 ORM / DB，避免数据被意外修改 |
| 可维护性 | 各层职责单一，改动互不影响 |
| 可测试性 | Unit Test 可单独测试每层逻辑 |
| 可扩展性 | 可轻松替换数据库、框架或接口协议 |
| 事务可控 | Service 层集中控制 commit / rollback |

---

## 8️⃣ 图示：数据流全景图

```
[User / Frontend]
       ↓
 ┌───────────────────┐
 │  Controller (客服) │ → InputDTO / OutputDTO
 └───────────────────┘
       ↓
 ┌───────────────────┐
 │   Service (经理)   │ → 事务控制、规则校验
 └───────────────────┘
       ↓
 ┌───────────────────┐
 │  DAO (仓库管理员)  │ → ORM 操作、SQL 查询
 └───────────────────┘
       ↓
 ┌───────────────────┐
 │ Database (仓库)   │ → 存储数据
 └───────────────────┘
```

---

## 9️⃣ Key Takeaways

✅ **Controller 不动数据库，只处理输入输出**

✅ **Service 统管逻辑与事务，是系统核心**

✅ **DAO 专注数据访问，是"仓库管理员"**

✅ **Database 是最终存储，不做业务逻辑**

✅ **DTO 是 Controller 与 Service 之间的防火墙**