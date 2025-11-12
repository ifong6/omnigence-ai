# Use Cases Document

## UC1 - Create Job

| **Attribute** | **Details** |
|---|---|
| **Use Case ID** | UC1 |
| **Use Case Name** | Create Job |
| **Primary Actor** | User |
| **Trigger** | 用户创建新项目 (User creates new project) |
| **Precondition** | 无 (None) |
| **Main Success Scenario (MSS)** | 1. 用户输入项目信息（客户、项目名、类型）<br>2. 系统生成唯一 Job No.<br>3. 保存 Job 记录 |
| **Extensions / Variants** | **E1**: 同日继续创建 Quotation（=UC2）<br>**E2**: 隔天/隔月再创建 Quotation<br>**E3**: 仅建 Job，不出报价 |
| **Postcondition / Output** | Job 被保存，状态为 Active |
| **AI Role / System Automation** | AI 自动生成 Job No.、建议字段填充 |

---

## UC2 - Create Quotation

| **Attribute** | **Details** |
|---|---|
| **Use Case ID** | UC2 |
| **Use Case Name** | Create Quotation |
| **Primary Actor** | User |
| **Trigger** | 用户创建报价单 (User creates quotation) |
| **Precondition** | 存在 Job（或由系统创建） |
| **Main Success Scenario (MSS)** | 1. 选择现有 Job → 生成 Quotation 草稿<br>2. 编辑报价项、金额、客户资料<br>3. 保存报价 |
| **Extensions / Variants** | **E1**: 若无 Job → include UC1 自动建 Job<br>**E2**: 多次报价（Job 延伸报价） |
| **Postcondition / Output** | Quotation 与 Job 关联、状态 Draft |
| **AI Role / System Automation** | AI 自动填充客户资料、金额范围建议 |

---

## UC3 - Update Job Info

| **Attribute** | **Details** |
|---|---|
| **Use Case ID** | UC3 |
| **Use Case Name** | Update Job Info |
| **Primary Actor** | User |
| **Trigger** | 修改项目信息 (Modify project information) |
| **Precondition** | Job 已存在 |
| **Main Success Scenario (MSS)** | 用户在系统中修改客户或项目信息并保存 |
| **Extensions / Variants** | extend UC6：AI 提醒其他关联 Job 是否同步修改 |
| **Postcondition / Output** | Job 信息更新并记录修改日志 |
| **AI Role / System Automation** | AI 检测重复客户、提醒更新关联 Job |

---

## UC4 - Update Quotation Info

| **Attribute** | **Details** |
|---|---|
| **Use Case ID** | UC4 |
| **Use Case Name** | Update Quotation Info |
| **Primary Actor** | User |
| **Trigger** | 修改报价信息 (Modify quotation information) |
| **Precondition** | Quotation 已存在 |
| **Main Success Scenario (MSS)** | 用户在系统中修改报价金额、描述或客户资料 |
| **Extensions / Variants** | extend UC7：AI 提醒其他 Quotation 是否同步 |
| **Postcondition / Output** | Quotation 记录更新并生成新版本 |
| **AI Role / System Automation** | AI 检测金额或条款变更，提示审批 |

---

## UC5 - Modify Quotation (in UI)

| **Attribute** | **Details** |
|---|---|
| **Use Case ID** | UC5 |
| **Use Case Name** | Modify Quotation (in UI) |
| **Primary Actor** | User |
| **Trigger** | 编辑报价内容 (Edit quotation content) |
| **Precondition** | Quotation 已存在 |
| **Main Success Scenario (MSS)** | 1. 打开报价界面<br>2. 修改内容<br>3. 保存为新版本 |
| **Extensions / Variants** | **E1**: 系统生成版本号 (V1/V2)<br>**E2**: 比对差异、保留旧版本 |
| **Postcondition / Output** | 更新成功，新版本生效 |
| **AI Role / System Automation** | AI 标记取消旧版、记录改动摘要 |

---

## UC6 - AI Reminder (related Job No.)

| **Attribute** | **Details** |
|---|---|
| **Use Case ID** | UC6 |
| **Use Case Name** | AI Reminder (related Job No.) |
| **Primary Actor** | AI Assistant |
| **Trigger** | Job 信息变更 (Job information changes) |
| **Precondition** | 系统检测到 Job 关系 |
| **Main Success Scenario (MSS)** | AI 检测同客户其他 Job 并提示用户 |
| **Extensions / Variants** | - |
| **Postcondition / Output** | 提示消息 / 通知 |
| **AI Role / System Automation** | 触发式提醒，减少信息不一致 |

---

## UC7 - AI Reminder (related Quotation No.)

| **Attribute** | **Details** |
|---|---|
| **Use Case ID** | UC7 |
| **Use Case Name** | AI Reminder (related Quotation No.) |
| **Primary Actor** | AI Assistant |
| **Trigger** | Quotation 信息变更 (Quotation information changes) |
| **Precondition** | 同一 Job 下存在多个报价 |
| **Main Success Scenario (MSS)** | AI 检测并提醒用户是否批量更新 |
| **Extensions / Variants** | - |
| **Postcondition / Output** | 提示消息 / 通知 |
| **AI Role / System Automation** | 智能识别同项目报价一致性问题 |

---

## UC8 - Weekly/Monthly Status Check

| **Attribute** | **Details** |
|---|---|
| **Use Case ID** | UC8 |
| **Use Case Name** | Weekly/Monthly Status Check |
| **Primary Actor** | AI Assistant |
| **Trigger** | 每周或每月定时任务 (Weekly or monthly scheduled task) |
| **Precondition** | 系统中存在报价和项目数据 |
| **Main Success Scenario (MSS)** | 1. AI 扫描所有 Job/Quotation 状态<br>2. 生成周/月报表（参考 survey.xlsx）<br>3. 标出异常项目 |
| **Extensions / Variants** | - |
| **Postcondition / Output** | 报表生成（CSV/Excel）并通知会计 |
| **AI Role / System Automation** | AI 自动分析状态、生成 summary、标红异常项 |

---

## UC9 - Export Quotation PDF (Read-only)

| **Attribute** | **Details** |
|---|---|
| **Use Case ID** | UC9 |
| **Use Case Name** | Export Quotation PDF (Read-only) |
| **Primary Actor** | User |
| **Trigger** | 用户点击"下载PDF" (User clicks "Download PDF") |
| **Precondition** | Quotation 已存在 |
| **Main Success Scenario (MSS)** | 系统导出报价单 PDF，不修改原数据 |
| **Extensions / Variants** | - |
| **Postcondition / Output** | PDF 文件下载成功 |
| **AI Role / System Automation** | AI 校验版本是否最新 |

---

## Summary

This document contains 9 use cases covering:
- Job and Quotation creation and management (UC1-UC5)
- AI-powered reminders and synchronization (UC6-UC7)
- Automated status reporting (UC8)
- Document export functionality (UC9)

The system integrates AI automation throughout to enhance efficiency, reduce errors, and maintain data consistency.