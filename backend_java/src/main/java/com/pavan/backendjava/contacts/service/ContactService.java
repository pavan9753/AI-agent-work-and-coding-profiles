package com.pavan.backendjava.contacts.service;

import java.time.Instant;
import java.util.Locale;

import org.springframework.dao.DuplicateKeyException;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import com.pavan.backendjava.contacts.api.ContactRequest;
import com.pavan.backendjava.contacts.api.ContactResponse;
import com.pavan.backendjava.contacts.domain.Contact;
import com.pavan.backendjava.contacts.repository.ContactRepository;

@Service
public class ContactService {

    private final ContactRepository contactRepository;

    public ContactService(ContactRepository contactRepository) {
        this.contactRepository = contactRepository;
    }

    public Page<ContactResponse> listContacts(Pageable pageable) {
        return contactRepository.findAll(pageable).map(this::toResponse);
    }

    public ContactResponse getContact(String id) {
        return toResponse(findContact(id));
    }

    public ContactResponse createContact(ContactRequest request) {
        String email = normalizeEmail(request.email());
        ensureEmailIsAvailable(email);

        Instant now = Instant.now();
        Contact contact = new Contact();
        applyRequest(contact, request, email);
        contact.setCreatedAt(now);
        contact.setUpdatedAt(now);
        return toResponse(saveContact(contact, email));
    }

    public ContactResponse updateContact(String id, ContactRequest request) {
        Contact contact = findContact(id);
        String email = normalizeEmail(request.email());

        if (!email.equalsIgnoreCase(contact.getEmail())) {
            ensureEmailIsAvailable(email);
        }

        applyRequest(contact, request, email);
        contact.setUpdatedAt(Instant.now());
        return toResponse(saveContact(contact, email));
    }

    public void deleteContact(String id) {
        Contact contact = findContact(id);
        contactRepository.delete(contact);
    }

    private Contact findContact(String id) {
        return contactRepository.findById(id).orElseThrow(() -> new ContactNotFoundException(id));
    }

    private void ensureEmailIsAvailable(String email) {
        contactRepository.findByEmailIgnoreCase(email).ifPresent(existing -> {
            throw new DuplicateContactEmailException(email);
        });
    }

    private Contact saveContact(Contact contact, String email) {
        try {
            return contactRepository.save(contact);
        } catch (DuplicateKeyException exception) {
            throw new DuplicateContactEmailException(email);
        }
    }

    private void applyRequest(Contact contact, ContactRequest request, String normalizedEmail) {
        contact.setFullName(request.fullName().trim());
        contact.setEmail(normalizedEmail);
        contact.setCompany(cleanOptionalText(request.company()));
        contact.setStatus(request.status());
        contact.setNotes(cleanOptionalText(request.notes()));
    }

    private String normalizeEmail(String email) {
        return email.trim().toLowerCase(Locale.ROOT);
    }

    private String cleanOptionalText(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        return value.trim();
    }

    private ContactResponse toResponse(Contact contact) {
        return new ContactResponse(
                contact.getId(),
                contact.getFullName(),
                contact.getEmail(),
                contact.getCompany(),
                contact.getStatus(),
                contact.getNotes(),
                contact.getCreatedAt(),
                contact.getUpdatedAt());
    }
}
