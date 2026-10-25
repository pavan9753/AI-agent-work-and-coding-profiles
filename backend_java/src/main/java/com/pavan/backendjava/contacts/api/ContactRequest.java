package com.pavan.backendjava.contacts.api;

import com.pavan.backendjava.contacts.domain.ContactStatus;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record ContactRequest(
        @NotBlank @Size(max = 100) String fullName,
        @NotBlank @Email @Size(max = 254) String email,
        @Size(max = 120) String company,
        @NotNull ContactStatus status,
        @Size(max = 1000) String notes) {
}
