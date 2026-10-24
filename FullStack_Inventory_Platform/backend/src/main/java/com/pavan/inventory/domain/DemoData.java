package com.pavan.inventory.domain;

import com.pavan.inventory.repository.InventoryRepository;
import java.math.BigDecimal;
import java.util.List;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DemoData {
    @Bean
    CommandLineRunner seedInventory(InventoryRepository repository) {
        return args -> {
            if (repository.count() == 0) {
                repository.saveAll(List.of(
                        new InventoryItem("Wireless keyboard", "ACC-104", "Accessories", new BigDecimal("49.00"), 34, 8),
                        new InventoryItem("USB-C dock", "ACC-118", "Accessories", new BigDecimal("129.00"), 7, 10),
                        new InventoryItem("27-inch monitor", "DSP-207", "Displays", new BigDecimal("329.00"), 18, 5),
                        new InventoryItem("Laptop stand", "ERG-310", "Ergonomics", new BigDecimal("68.50"), 4, 6),
                        new InventoryItem("Noise-canceling headset", "AUD-412", "Audio", new BigDecimal("179.00"), 21, 6),
                        new InventoryItem("Webcam", "VID-506", "Video", new BigDecimal("89.00"), 12, 4)));
            }
        };
    }
}
