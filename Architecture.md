## Architecture

![HLD Architecture](images/hld.svg)

## Services

| Service       | Description                                   |
| ------------- | --------------------------------------------- |
| FCI API       | The main API for the FCI platform             |
| FCI Dashboard | The dashboard for the FCI platform            |
| Mock Services | The mock services for the FCI platform        |
| Simulator     | The simulator for the FCI platform            |
| Ingestion     | The ingestion service for the FCI platform    |
| Insights      | The insights service for the FCI platform     |
| Notification  | The notification service for the FCI platform |

## Data Flow

Current data flow is as follows:

1.  Mock Services send 500 errors to the FCI API using simulater script
2.  FCI API ingests the failures into the database
3.  FCI API analyzes the failures and creates incidents
4.  FCI API sends the incidents to the Insights service
5.  Insights service analyzes the incidents and creates insights
