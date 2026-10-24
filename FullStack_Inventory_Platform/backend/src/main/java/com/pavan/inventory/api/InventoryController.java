package com.pavan.inventory.api;

import com.pavan.inventory.service.InventoryService;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.List;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "${app.cors.allowed-origin:http://localhost:5173}")
public class InventoryController {
    private final InventoryService service;
    public InventoryController(InventoryService service) { this.service = service; }

    @GetMapping("/items")
    public List<ItemResponse> list(@RequestParam(required = false) String q) { return service.list(q); }

    @GetMapping("/items/{id}")
    public ItemResponse get(@PathVariable UUID id) { return service.get(id); }

    @PostMapping("/items")
    public ResponseEntity<ItemResponse> create(@Valid @RequestBody ItemRequest request) {
        ItemResponse created = service.create(request);
        return ResponseEntity.created(URI.create("/api/items/" + created.id())).body(created);
    }

    @PutMapping("/items/{id}")
    public ItemResponse update(@PathVariable UUID id, @Valid @RequestBody ItemRequest request) { return service.update(id, request); }

    @DeleteMapping("/items/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) { service.delete(id); return ResponseEntity.noContent().build(); }

    @GetMapping("/dashboard")
    public DashboardResponse dashboard() { return service.dashboard(); }
}
