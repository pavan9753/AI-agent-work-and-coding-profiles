package com.pavan.inventory.repository;

import com.pavan.inventory.domain.InventoryItem;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface InventoryRepository extends JpaRepository<InventoryItem, UUID> {
    List<InventoryItem> findByNameContainingIgnoreCaseOrSkuContainingIgnoreCaseOrCategoryContainingIgnoreCase(
            String name, String sku, String category);
    boolean existsBySkuIgnoreCase(String sku);
    boolean existsBySkuIgnoreCaseAndIdNot(String sku, UUID id);
}
