package org.example.week2.service;

import lombok.RequiredArgsConstructor;
import org.example.week2.dto.*;
import org.example.week2.exception.NotFoundException;
import org.example.week2.mapper.UserMapper;
import org.example.week2.model.User;
import org.example.week2.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final UserMapper userMapper;

    public List<UserResponse> getAllUsers() {

        return userRepository.findAll()
                .stream()
                .map(userMapper::toResponse)
                .collect(Collectors.toList());
    }

    public UserResponse getUserById(Long id) {

        User user = userRepository.findById(id)
                .orElseThrow(() -> new NotFoundException("Not found"));

        return userMapper.toResponse(user);
    }

    public UserResponse createUser(UserCreateRequest request) {

        User user = User.builder()
                .username(request.getUsername())
                .email(request.getEmail())
                .build();

        return userMapper.toResponse(userRepository.save(user));
    }

    public UserResponse updateUser(Long id, UserUpdateRequest request) {

        User user = userRepository.findById(id)
                .orElseThrow(() -> new NotFoundException("Not found"));

        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());

        return userMapper.toResponse(userRepository.save(user));
    }

    public UserResponse patchUser(Long id, UserPatchRequest request) {

        User user = userRepository.findById(id)
                .orElseThrow(() -> new NotFoundException("Not found"));

        if (request.getUsername() != null) {
            user.setUsername(request.getUsername());
        }

        if (request.getEmail() != null) {
            user.setEmail(request.getEmail());
        }

        return userMapper.toResponse(userRepository.save(user));
    }

    public void deleteUser(Long id) {

        User user = userRepository.findById(id)
                .orElseThrow(() -> new NotFoundException("Not found"));

        userRepository.delete(user);
    }

}