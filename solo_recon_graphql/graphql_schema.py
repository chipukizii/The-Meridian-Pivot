# solo_recon_graphql/graphql_schema.py
# Day 1-2 Solo Recon Mini-Prototype: GraphQL Inventory Schema
# Purpose: Allow flexible query and mutation capability over Northstar Retail Co. stock inventory.

import os
import sys

# Ensure parent directory is in sys.path to access db.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import db

import graphene


class InventoryItemType(graphene.ObjectType):
    sku = graphene.String(required=True)
    name = graphene.String(required=True)
    category = graphene.String()
    price = graphene.String()
    in_stock = graphene.Boolean()
    stock_count = graphene.Int()
    sizes_available = graphene.List(graphene.String)
    out_of_stock_sizes = graphene.List(graphene.String)
    next_restock_date = graphene.String()

    def resolve_in_stock(root, info):
        return root.get('inStock', False)

    def resolve_stock_count(root, info):
        return root.get('stockCount', 0)

    def resolve_sizes_available(root, info):
        return root.get('sizesAvailable', [])

    def resolve_out_of_stock_sizes(root, info):
        return root.get('outOfStockSizes', [])

    def resolve_next_restock_date(root, info):
        return root.get('nextRestockDate', '')


class StockCheckResultType(graphene.ObjectType):
    sku = graphene.String(required=True)
    available = graphene.Boolean(required=True)
    stock_count = graphene.Int(required=True)
    message = graphene.String()


class Query(graphene.ObjectType):
    inventory = graphene.List(
        InventoryItemType,
        query=graphene.String(default_value=""),
        description="Search inventory items by keyword matching name, sku, or category."
    )
    item_by_sku = graphene.Field(
        InventoryItemType,
        sku=graphene.String(required=True),
        description="Fetch a single inventory item by exact SKU."
    )
    check_stock = graphene.Field(
        StockCheckResultType,
        sku=graphene.String(required=True),
        requested_quantity=graphene.Int(default_value=1),
        description="Check real-time stock availability for a given SKU and requested quantity."
    )

    def resolve_inventory(root, info, query=""):
        items = db.search_inventory(query)
        return items

    def resolve_item_by_sku(root, info, sku):
        item = db.get_item_by_sku(sku)
        return item

    def resolve_check_stock(root, info, sku, requested_quantity=1):
        item = db.get_item_by_sku(sku)
        if not item:
            return StockCheckResultType(
                sku=sku,
                available=False,
                stock_count=0,
                message=f"Item with SKU '{sku}' not found."
            )
        stock_count = item.get('stockCount', 0)
        is_available = item.get('inStock', False) and stock_count >= requested_quantity
        msg = f"In stock: {stock_count} units available." if is_available else f"Out of stock or insufficient quantity (Requested: {requested_quantity}, Available: {stock_count})."
        return StockCheckResultType(
            sku=sku,
            available=is_available,
            stock_count=stock_count,
            message=msg
        )


class UpdateStockMutation(graphene.Mutation):
    class Arguments:
        sku = graphene.String(required=True)
        new_count = graphene.Int(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    item = graphene.Field(InventoryItemType)

    def mutate(root, info, sku, new_count):
        item = db.get_item_by_sku(sku)
        if not item:
            return UpdateStockMutation(
                success=False,
                message=f"SKU '{sku}' not found.",
                item=None
            )
        # Update in-memory / JSON dict representation
        item['stockCount'] = new_count
        item['inStock'] = new_count > 0
        return UpdateStockMutation(
            success=True,
            message=f"Successfully updated SKU '{sku}' stock count to {new_count}.",
            item=item
        )


class Mutation(graphene.ObjectType):
    update_stock = UpdateStockMutation.Field(description="Update stock count for an inventory SKU.")


schema = graphene.Schema(query=Query, mutation=Mutation)
