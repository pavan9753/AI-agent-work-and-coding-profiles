package com.pavan.inventory.api;

import com.pavan.inventory.domain.InventoryItem;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

public record ItemResponse(UUID id, String name, String sku, String category, BigDecimal unitPrice,
                          int quantity, int reorderThreshold, boolean lowStock, Instant updatedAt) {
    public static ItemResponse from(InventoryItem item) {
        return new ItemResponse(item.getId(), item.getName(), item.getSku(), item.getCategory(), item.getUnitPrice(),
                item.getQuantity(), item.getReorderThreshold(), item.getQuantity() <= item.getReorderThreshold(), item.getUpdatedAt());
    }
}
