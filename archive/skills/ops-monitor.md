---
name: ops-monitor
description: 維運監控與異常處理建議助理 - 依系統 LOG 提供風險警示與解決方案
skill_type: agent
trigger: 當需要監控系統、分析 LOG、異常告警、提供維運建議時使用
---

# 維運監控與異常處理建議助理

## 功能目標
- 即時監控系統 LOG 與效能指標
- 依工作說明（SOP）自動判斷風險
- 整合週邊系統狀態
- 提早警示潛在問題
- 異常發生時提供診斷與解決方案
- 降低 MTTR (Mean Time To Resolve) 60% 以上

## 使用方式
```
/ops-monitor [--source <LOG來源>] [--mode <監控|分析|診斷>] [--alert-level <等級>]
```

## 處理流程
1. **LOG 收集與解析**
   - 即時串接多種 LOG 來源（App, DB, API, Infra）
   - 結構化非結構化 LOG
   - 時間序列索引
   - 關聯分析

2. **基準比對**
   - 載入 SOP 與效能基準（如 JOB 應 30 分內完成）
   - 建立正常行為模型
   - 識別偏離基準的異常
   - 計算異常嚴重度

3. **智能分析**
   - 模式識別（重複錯誤、趨勢異常）
   - 根因分析（Root Cause Analysis）
   - 影響範圍評估
   - 預測性維運（提早發現潛在問題）

4. **週邊系統整合**
   - 檢查相依系統狀態
   - 串接 API health check
   - 資料庫連線監控
   - 第三方服務可用性

5. **告警與建議**
   - 分級告警（Critical / Warning / Info）
   - 自動通知相關人員
   - 提供診斷步驟
   - 推薦解決方案與 Runbook

6. **自動化回應**（選用）
   - 執行預定義修復腳本
   - 自動重啟失敗服務
   - 切換備援系統
   - 記錄所有自動化行為

## 監控場景範例

### 場景 1: JOB 執行時間異常
```markdown
## ⚠️ 警示通知

**時間**: 2026-05-28 03:45:23  
**等級**: 🟡 Warning  
**系統**: Data ETL Pipeline

### 問題描述
JOB `daily_sales_aggregation` 執行時間超過基準

**基準**: 30 分鐘  
**實際**: 47 分鐘  
**偏離**: +56.7%

### 根因分析
1. **資料量異常增長**
   - 今日處理記錄: 5.2M (平均: 3.1M)
   - 增長原因: 促銷活動導致訂單量激增

2. **資料庫效能下降**
   - Query time p95: 850ms (平時: 320ms)
   - 慢查詢 LOG: 發現 15 個 slow queries
   - 缺少索引: `orders.created_at` 欄位

### 影響評估
- ✅ JOB 已完成，資料一致性正常
- ⚠️ 下游報表延遲 17 分鐘
- ⚠️ 若持續增長，可能影響白天業務時段

### 建議解決方案

**立即處理**:
1. 新增資料庫索引
   ```sql
   CREATE INDEX idx_orders_created_at ON orders(created_at);
   ```

2. 檢查執行計畫
   ```bash
   EXPLAIN ANALYZE SELECT ...
   ```

**中期優化**:
1. 實作增量處理而非全量
2. 考慮分批處理大量資料
3. 評估 database sharding

**長期規劃**:
1. 升級資料庫規格（考慮 scale-up）
2. 引入 cache layer 減少查詢負擔

### Runbook
📘 參考: [ETL Performance Tuning Guide](./docs/runbook/etl-tuning.md)

### 後續追蹤
- [ ] 執行索引優化
- [ ] 監控明日執行時間
- [ ] 評估長期方案可行性
```

---

### 場景 2: API 錯誤率飆升
```markdown
## 🔴 緊急警示

**時間**: 2026-05-28 14:23:11  
**等級**: 🔴 Critical  
**系統**: Payment API

### 問題描述
支付 API 錯誤率異常飆升

**正常錯誤率**: <0.1%  
**當前錯誤率**: 12.3%  
**影響**: 約 500 筆交易失敗

### 即時狀況
```
[14:20:15] ERROR: Connection timeout to payment-gateway.example.com
[14:20:18] ERROR: Connection timeout to payment-gateway.example.com
[14:20:21] ERROR: Connection timeout to payment-gateway.example.com
[14:23:05] ERROR: java.net.SocketTimeoutException: Read timed out
```

### 根因判斷
✅ **已排除**:
- 應用程式記憶體正常 (65% used)
- CPU 使用率正常 (42%)
- 資料庫連線池正常 (23/100 active)

⚠️ **疑似原因**:
1. **第三方支付閘道異常**
   - 連線逾時率: 98%
   - 平均回應時間: >30s (正常: 800ms)
   - 閘道狀態頁面: 🔴 Degraded Performance

2. **網路問題**
   - Ping payment-gateway: 23% packet loss
   - Traceroute: 異常 hop at ISP level

### 週邊系統狀態
- 🟢 Database: Normal
- 🟢 Redis Cache: Normal
- 🔴 Payment Gateway: **Degraded**
- 🟡 Notification Service: Slight delay

### 建議處理步驟

**緊急處置** (5分鐘內):
1. ✅ 啟用備援支付閘道
   ```bash
   kubectl set env deployment/payment-api PAYMENT_PROVIDER=backup
   kubectl rollout restart deployment/payment-api
   ```

2. ✅ 發送客戶通知
   - 告知使用者系統維護中
   - 提供替代支付方式

**後續處理**:
1. 聯繫主要支付閘道廠商確認狀況
2. 記錄受影響交易，待系統恢復後重試
3. 檢視 SLA 與賠償機制

**事後檢討**:
- 評估雙閘道自動切換機制
- 調整健康檢查與 circuit breaker 閾值
- 更新監控告警規則

### 聯絡資訊
- On-call Engineer: @john.doe (已通知)
- Payment Provider Support: support@payment.example.com
- 事件追蹤: INC-2026-0528-001

### 時間軸
- 14:20 問題開始
- 14:23 系統自動告警
- 14:25 手動切換備援閘道
- 14:28 錯誤率降至 0.5%
- 14:35 系統恢復正常
```

---

### 場景 3: 預測性維運
```markdown
## 💡 優化建議

**時間**: 2026-05-28 09:00:00  
**等級**: 🟢 Info  
**系統**: Web Application

### 趨勢分析
系統發現以下趨勢，建議提前處理：

#### 1. 磁碟空間使用趨勢
**當前狀態**: 🟡 注意
- 當前使用: 68%
- 30天前: 45%
- **增長率**: 約 0.8% / 天
- **預測**: 40 天後將達 85% (告警閾值)

**建議**:
- 規劃磁碟清理或擴容
- 檢查 LOG rotation 設定
- 評估舊資料歸檔策略

#### 2. 記憶體洩漏跡象
**當前狀態**: 🟡 注意
- JVM Heap 使用持續緩慢增長
- GC 頻率增加 15%
- 老年代使用率: 82%

**建議**:
- 執行 heap dump 分析
- 檢查是否有記憶體洩漏
- 規劃應用程式重啟時間

#### 3. API 回應時間增長
**趨勢**: p95 latency 過去 7 天增長 12%
- 一週前: 280ms
- 今日: 314ms

**可能原因**:
- 資料量增長
- 快取命中率下降 (88% → 82%)
- 慢查詢增加

**建議**:
- 檢視快取策略
- 分析慢查詢 LOG
- 考慮資料庫索引優化
```

## 技術架構

### LOG 來源整合
- Application: Log4j, Winston, Python logging
- Infrastructure: Syslog, journald
- Container: Docker logs, Kubernetes events
- Database: MySQL slow query log, PostgreSQL logs
- Web Server: Nginx access/error logs

### 分析引擎
- 即時串流: Apache Kafka, Fluentd
- 儲存: Elasticsearch, ClickHouse
- 視覺化: Grafana, Kibana
- AI 分析: Claude API, Anomaly Detection ML models

### 告警整合
- PagerDuty
- Slack / Microsoft Teams
- Email / SMS
- Webhook (自訂整合)

## 設定範例

```yaml
# ops-monitor-config.yaml
monitors:
  - name: etl_job_duration
    type: threshold
    source: app_logs
    pattern: "JOB.*completed"
    metric: duration_minutes
    threshold:
      warning: 30
      critical: 45
    sop: "ETL jobs should complete within 30 minutes"
    runbook_url: "https://wiki/runbook/etl"
    
  - name: api_error_rate
    type: anomaly
    source: api_logs
    metric: error_rate
    baseline: 0.1  # 0.1%
    sensitivity: high
    alert_on: 3x_baseline
    
  - name: disk_usage_prediction
    type: predictive
    source: system_metrics
    metric: disk_usage_percent
    forecast_days: 30
    alert_threshold: 85

integrations:
  - type: pagerduty
    api_key: ${PAGERDUTY_KEY}
    severity_mapping:
      critical: trigger
      warning: acknowledge
      
  - type: slack
    webhook: ${SLACK_WEBHOOK}
    channel: "#ops-alerts"
```

## 最佳實踐
- 建立完整的 Runbook 文件庫
- 定期檢討告警規則（避免 alert fatigue）
- 實作自動化修復腳本
- 進行定期災難演練
- 保留完整的審計軌跡
