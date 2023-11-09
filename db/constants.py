from datetime import date
from utils.configloader import ConfigUtil

AI_BUDGET_TABLE = ConfigUtil.getInstance().configJSON["db.budgetTable"]
AI_PREDICTIONS_TABLE = ConfigUtil.getInstance().configJSON["db.predictionsTable"]

INSERT_AI_BUDGET_SQL = "INSERT INTO %s (CustomerID, Week, AllocatedAmount, CategoryTypeCode, Spending) values(?,?,?,?,?)" %AI_BUDGET_TABLE

INSERT_AI_PREDICTIONS_SQL = "INSERT INTO %s (CustomerID, CategoryTypeCode, Week, Spending, AllocatedAmount, ExceedAlert) values(?,?,?,?,?,?)" %AI_PREDICTIONS_TABLE
