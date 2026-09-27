QUantumSrc/
├── src/
│   ├── main.cpp
│   ├── engine/
│   │   ├── Engine.cpp
│   │   ├── Engine.hpp
│   │   ├── Renderer.cpp
│   │   ├── Renderer.hpp
│   │   ├── Input.cpp
│   │   └── Input.hpp
│   ├── game/
│   │   ├── Game.cpp
│   │   └── Game.hpp
│   └── math/
│       ├── Vector3.hpp
│       └── Matrix4.hpp
├── include/
├── assets/
├── games/
├── mods/
├── Makefile
└── README.md

  #include <SDL.h>
#include <iostream>

class Engine {
public:
    bool init()
    {
        if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_EVENTS) != 0) {
            std::cerr << "SDL_Init failed: "
                      << SDL_GetError() << '\n';
            return false;
        }

        window = SDL_CreateWindow(
            "QUantumSrc",
            SDL_WINDOWPOS_CENTERED,
            SDL_WINDOWPOS_CENTERED,
            1280,
            720,
            SDL_WINDOW_SHOWN
        );

        if (!window) {
            std::cerr << "SDL_CreateWindow failed: "
                      << SDL_GetError() << '\n';
            return false;
        }

        renderer = SDL_CreateRenderer(
            window,
            -1,
            SDL_RENDERER_ACCELERATED |
            SDL_RENDERER_PRESENTVSYNC
        );

        if (!renderer) {
            std::cerr << "SDL_CreateRenderer failed: "
                      << SDL_GetError() << '\n';
            return false;
        }

        return true;
    }

    void run()
    {
        bool running = true;
        SDL_Event event{};

        while (running) {
            while (SDL_PollEvent(&event)) {
                if (event.type == SDL_QUIT)
                    running = false;

                if (event.type == SDL_KEYDOWN &&
                    event.key.keysym.sym == SDLK_ESCAPE) {
                    running = false;
                }
            }

            SDL_SetRenderDrawColor(renderer, 20, 20, 24, 255);
            SDL_RenderClear(renderer);

            // QUantumSrc rendering goes here.

            SDL_RenderPresent(renderer);
        }
    }

    void shutdown()
    {
        if (renderer)
            SDL_DestroyRenderer(renderer);

        if (window)
            SDL_DestroyWindow(window);

        SDL_Quit();
    }

private:
    SDL_Window* window = nullptr;
    SDL_Renderer* renderer = nullptr;
};

int main()
{
    Engine engine;

    if (!engine.init())
        return 1;

    engine.run();
    engine.shutdown();

    return 0;
}
