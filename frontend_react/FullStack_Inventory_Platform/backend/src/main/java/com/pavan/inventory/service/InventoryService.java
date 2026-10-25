package com.pavan.inventory.service;

import com.pavan.inventory.api.DashboardResponse;
import com.pavan.inventory.api.ItemRequest;
import com.pavan.inventory.api.ItemResponse;
import com.pavan.inventory.domain.InventoryItem;
import com.pavan.inventory.repository.InventoryRepository;
import java.math.BigDecimal;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional
public class InventoryService {
    private final InventoryRepository repository;

    public InventoryService(InventoryRepository repository) { this.repository = repository; }

    @Transactional(readOnly = true)
    public List<ItemResponse> list(String query) {
        List<InventoryItem> items = query == null || query.isBlank()
                ? repository.findAll()
                : repository.findByNameContainingIgnoreCaseOrSkuContainingIgnoreCaseOrCategoryContainingIgnoreCase(
                        query.trim(), query.trim(), query.trim());
        return items.stream().sorted(Comparator.comparing(InventoryItem::getName, String.CASE_INSENSITIVE_ORDER))
                .map(ItemResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public ItemResponse get(UUID id) { return ItemResponse.from(find(id)); }

    public ItemResponse create(ItemRequest request) {
        if (repository.existsBySkuIgnoreCase(request.sku().trim())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "A product with this SKU already exists.");
        }
        return ItemResponse.from(repository.save(new InventoryItem(request.name(), request.sku(), request.category(),
                request.unitPrice(), request.quantity(), request.reorderThreshold())));
    }

    public ItemResponse update(UUID id, ItemRequest request) {
        InventoryItem item = find(id);
        if (repository.existsBySkuIgnoreCaseAndIdNot(request.sku().trim(), id)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "A product with this SKU already exists.");
        }
        item.update(request.name(), request.sku(), request.category(), request.unitPrice(),
                request.quantity(), request.reorderThreshold());
        return ItemResponse.from(repository.save(item));
    }

    public void delete(UUID id) { repository.delete(find(id)); }

    @Transactional(readOnly = true)
    public DashboardResponse dashboard() {
        List<InventoryItem> items = repository.findAll();
        long lowStock = items.stream().filter(item -> item.getQuantity() <= item.getReorderThreshold()).count();
        long units = items.stream().mapToLong(InventoryItem::getQuantity).sum();
        BigDecimal value = items.stream().map(item -> item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        return new DashboardResponse(items.size(), lowStock, units, value);
    }

    private InventoryItem find(UUID id) {
        return repository.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Product not found."));
    }
}
