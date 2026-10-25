package com.pavan.inventory.api;

import java.math.BigDecimal;

public record DashboardResponse(long productCount, long lowStockCount, long unitsInStock, BigDecimal inventoryValue) { }
