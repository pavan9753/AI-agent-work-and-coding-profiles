package com.pavan.inventory.api;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;

public record ItemRequest(
        @NotBlank @Size(max = 120) String name,
        @NotBlank @Size(max = 40) String sku,
        @NotBlank @Size(max = 60) String category,
        @NotNull @DecimalMin("0.00") BigDecimal unitPrice,
        @Min(0) int quantity,
        @Min(0) int reorderThreshold) { }
