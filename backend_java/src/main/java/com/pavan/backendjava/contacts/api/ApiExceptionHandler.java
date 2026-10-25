package com.pavan.backendjava.contacts.api;

import java.time.Instant;
import java.util.Map;
import java.util.TreeMap;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import com.pavan.backendjava.contacts.service.ContactNotFoundException;
import com.pavan.backendjava.contacts.service.DuplicateContactEmailException;

import jakarta.servlet.http.HttpServletRequest;

@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(ContactNotFoundException.class)
    public ResponseEntity<ApiError> handleNotFound(ContactNotFoundException exception, HttpServletRequest request) {
        return error(HttpStatus.NOT_FOUND, exception.getMessage(), request.getRequestURI(), Map.of());
    }

    @ExceptionHandler(DuplicateContactEmailException.class)
    public ResponseEntity<ApiError> handleDuplicateEmail(
            DuplicateContactEmailException exception, HttpServletRequest request) {
        return error(HttpStatus.CONFLICT, exception.getMessage(), request.getRequestURI(), Map.of());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiError> handleValidation(
            MethodArgumentNotValidException exception, HttpServletRequest request) {
        Map<String, String> validationErrors = new TreeMap<>();
        exception.getBindingResult().getFieldErrors().forEach(fieldError ->
                validationErrors.putIfAbsent(fieldError.getField(), fieldError.getDefaultMessage()));
        return error(HttpStatus.BAD_REQUEST, "Request validation failed", request.getRequestURI(), validationErrors);
    }

    @ExceptionHandler(NoResourceFoundException.class)
    public ResponseEntity<ApiError> handleMissingRoute(NoResourceFoundException exception, HttpServletRequest request) {
        return error(HttpStatus.NOT_FOUND, "Route was not found", request.getRequestURI(), Map.of());
    }

    private ResponseEntity<ApiError> error(
            HttpStatus status, String message, String path, Map<String, String> validationErrors) {
        ApiError body = new ApiError(Instant.now(), status.value(), status.getReasonPhrase(), message, path,
                validationErrors);
        return ResponseEntity.status(status).body(body);
    }

    public record ApiError(
            Instant timestamp,
            int status,
            String error,
            String message,
            String path,
            Map<String, String> validationErrors) {
    }
}
