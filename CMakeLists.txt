make              # Debug build
make debug        # Debug build
make release      # Optimized release build
make run          # Build and run
make clean        # Remove build files
make rebuild      # Clean + build

CXX      := g++
CXXFLAGS := -std=c++20 -Wall -Wextra -Wpedantic
LDFLAGS  :=
LDLIBS   :=

TARGET   := engine

SRC_DIR  := src
BUILD_DIR := build
BIN_DIR  := bin

SOURCES  := $(shell find $(SRC_DIR) -name '*.cpp')
OBJECTS  := $(SOURCES:$(SRC_DIR)/%.cpp=$(BUILD_DIR)/%.o)
DEPS     := $(OBJECTS:.o=.d)

DEBUG_FLAGS   := -g -O0
RELEASE_FLAGS := -O2 -DNDEBUG

.PHONY: all debug release run clean rebuild

all: debug

debug: CXXFLAGS += $(DEBUG_FLAGS)
debug: $(BIN_DIR)/$(TARGET)

release: CXXFLAGS += $(RELEASE_FLAGS)
release: $(BIN_DIR)/$(TARGET)

$(BIN_DIR)/$(TARGET): $(OBJECTS)
	@mkdir -p $(dir $@)
	$(CXX) $(LDFLAGS) $^ $(LDLIBS) -o $@

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -MMD -MP -c $< -o $@

run: debug
	./$(BIN_DIR)/$(TARGET)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)

rebuild: clean all

-include $(DEPS)
