package com.pavan.inventory.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "inventory_items", uniqueConstraints = @UniqueConstraint(name = "uk_inventory_sku", columnNames = "sku"))
public class InventoryItem {
    @Id
    @GeneratedValue
    private UUID id;

    @Column(nullable = false, length = 120)
    private String name;

    @Column(nullable = false, length = 40)
    private String sku;

    @Column(nullable = false, length = 60)
    private String category;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal unitPrice;

    @Column(nullable = false)
    private int quantity;

    @Column(nullable = false)
    private int reorderThreshold;

    @Column(nullable = false)
    private Instant updatedAt;

    protected InventoryItem() { }

    public InventoryItem(String name, String sku, String category, BigDecimal unitPrice, int quantity, int reorderThreshold) {
        this.name = clean(name);
        this.sku = clean(sku).toUpperCase();
        this.category = clean(category);
        this.unitPrice = unitPrice;
        this.quantity = quantity;
        this.reorderThreshold = reorderThreshold;
    }

    @PrePersist
    @PreUpdate
    void touch() { updatedAt = Instant.now(); }

    private static String clean(String value) { return value == null ? null : value.trim(); }

    public UUID getId() { return id; }
    public String getName() { return name; }
    public String getSku() { return sku; }
    public String getCategory() { return category; }
    public BigDecimal getUnitPrice() { return unitPrice; }
    public int getQuantity() { return quantity; }
    public int getReorderThreshold() { return reorderThreshold; }
    public Instant getUpdatedAt() { return updatedAt; }

    public void update(String name, String sku, String category, BigDecimal unitPrice, int quantity, int reorderThreshold) {
        this.name = clean(name);
        this.sku = clean(sku).toUpperCase();
        this.category = clean(category);
        this.unitPrice = unitPrice;
        this.quantity = quantity;
        this.reorderThreshold = reorderThreshold;
    }
}
