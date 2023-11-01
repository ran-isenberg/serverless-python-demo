{
    "Comment": "This state machine returns an employee entry from DynamoDB",
    "StartAt": "Store test event",
    "States": {
        "Store test event": {
            "Type": "Task",
            "Resource": "arn:aws:states:::dynamodb:putItem",
            "Parameters": {
                "TableName": "${TABLE_NAME}",
                "Item": {
                    "pk": {
                        "S.$": "$.detail.metadata.event_source"
                    },
                    "sk": {
                        "S.$": "States.Format('{}#{}#{}', $.id, $.detail.metadata.event_name, $.detail.metadata.created_at)"
                    },
                    "receipt_id": {
                        "S.$": "$.id"
                    },
                    "metadata": {
                        "S.$": "States.JsonToString($.detail.metadata)"
                    },
                    "data": {
                        "S.$": "States.JsonToString($.detail.data)"
                    }
                }
            },
            "ResultPath": "$.output",
            "End": true
        }
    }
}
