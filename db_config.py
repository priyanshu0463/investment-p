from dataclasses import dataclass

@dataclass
class DBConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "stock_analysis"
    user: str = "admin"
    password: str = "Password123"  # Change this or use environment variables 
