

TB1:

end to end pipeline

heartbeat

RED metrics

U of USE metric

only 1 env support

conection state detection

platform_health(سناریو های شکست خود سیستم)






TB1_RM: (NOT COMPLETED yet❌)

1. proto ➖
      ↓
2. schemas ➖
      ↓
3. agent ✅
      ↓
4. sample_service ✅
      ↓
5. SDK ✅
      ↓
6. SDK ↔ Agent
      ↓
7. Control Plane
      └── memory_recorder
      ↓
8. Agent ↔ Control Plane
      ↓
9. SDK ↔ Control Plane
      └── heartbeat
      ↓
10. Control Plane
       ├── detection
       └── platform_health




for runnig🔥: 

terminal: 

docker desktop start 

docker-compose up -d --build