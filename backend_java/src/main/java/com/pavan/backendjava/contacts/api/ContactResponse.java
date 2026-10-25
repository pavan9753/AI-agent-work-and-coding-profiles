package com.pavan.backendjava.contacts.api;

import java.time.Instant;

import com.pavan.backendjava.contacts.domain.ContactStatus;

public record ContactResponse(
        String id,
        String fullName,
        String email,
        String company,
        ContactStatus status,
        String notes,
        Instant createdAt,
        Instant updatedAt) {
}
