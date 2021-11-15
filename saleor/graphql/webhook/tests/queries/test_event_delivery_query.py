import graphene

from .....core import EventDeliveryStatus
from .....webhook.event_types import WebhookEventType
from ....tests.utils import get_graphql_content

EVENT_DELIVERY_QUERY = """
    query webhook(
      $id: ID!
      $first: Int, $last: Int, $after: String, $before: String,
    ){
      webhook(id: $id){
        deliveries(
            first: $first, last: $last, after: $after, before: $before,
        ){
           edges{
             node{
               status
               eventType
               id
               attempts{
                 id
                 duration
                 response
                 requestHeaders
                 responseHeaders
                 }
            }
          }
        }
      }
    }
"""


def test_webhook_delivery_attempt_query(
    event_attempt, staff_api_client, permission_manage_apps
):
    # given
    webhook_id = graphene.Node.to_global_id(
        "Webhook", event_attempt.delivery.webhook.pk
    )
    staff_api_client.user.user_permissions.add(permission_manage_apps)
    variables = {"id": webhook_id, "first": 3}
    delivery = event_attempt.delivery
    delivery_id = graphene.Node.to_global_id("EventDelivery", delivery.pk)

    # when
    response = staff_api_client.post_graphql(EVENT_DELIVERY_QUERY, variables=variables)
    content = get_graphql_content(response)
    delivery_response = content["data"]["webhook"]["deliveries"]["edges"][0]["node"]
    attempts_response = delivery_response["attempts"]

    # then
    assert delivery_response["id"] == delivery_id
    assert delivery_response["status"] == EventDeliveryStatus.PENDING.upper()
    assert delivery_response["eventType"] == WebhookEventType.ANY.upper()
    assert len(attempts_response) == 1
    assert attempts_response[0]["response"] == event_attempt.response
    assert attempts_response[0]["duration"] is None
    assert attempts_response[0]["requestHeaders"] is None
    assert attempts_response[0]["responseHeaders"] is None
