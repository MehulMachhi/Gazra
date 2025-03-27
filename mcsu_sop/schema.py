import graphene
import graphql_jwt
import initiatives.schema

class Query(initiatives.schema.Query, graphene.ObjectType):
    # JWT Token verification
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

class Mutation(initiatives.schema.Mutation, graphene.ObjectType):
    # JWT Authentication
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

# Create schema
schema = graphene.Schema(query=Query, mutation=Mutation)