```java
package engine.graphics.opengl;

import com.sun.jna.*;
import com.sun.jna.ptr.PointerByReference;

import java.util.HashMap;
import java.util.Map;

public final class GLLoader {

    private GLLoader() {}

    private static final Map<String, Pointer> functions = new HashMap<>();

    /*
     * -------------------------------------------------------------------------
     * Native libraries
     * -------------------------------------------------------------------------
     */

    interface WindowsGL extends Library {
        WindowsGL INSTANCE =
                Native.load("opengl32", WindowsGL.class);

        Pointer wglGetProcAddress(String name);
    }

    interface LinuxGL extends Library {
        LinuxGL INSTANCE =
                Native.load("GL", LinuxGL.class);

        Pointer glXGetProcAddressARB(byte[] name);
    }

    interface MacGL extends Library {
        MacGL INSTANCE =
                Native.load("OpenGL", MacGL.class);
    }

    /*
     * -------------------------------------------------------------------------
     * Platform detection
     * -------------------------------------------------------------------------
     */

    private static final String OS =
            System.getProperty("os.name").toLowerCase();

    private static boolean isWindows() {
        return OS.contains("win");
    }

    private static boolean isLinux() {
        return OS.contains("linux");
    }

    private static boolean isMacOS() {
        return OS.contains("mac");
    }

    /*
     * -------------------------------------------------------------------------
     * Function loading
     * -------------------------------------------------------------------------
     */

    public static boolean load() {
        functions.clear();

        return loadCoreFunctions();
    }

    private static Pointer getProcAddress(String name) {

        Pointer address = null;

        if (isWindows()) {
            address = WindowsGL.INSTANCE.wglGetProcAddress(name);

            /*
             * Windows may return special invalid values for functions
             * that aren't available.
             */
            if (address != null) {
                long value = Pointer.nativeValue(address);

                if (value == 1 ||
                    value == 2 ||
                    value == 3 ||
                    value == 0xFFFFFFFFL) {
                    address = null;
                }
            }
        }

        else if (isLinux()) {
            byte[] bytes = (name + "\0").getBytes();

            address = LinuxGL.INSTANCE.glXGetProcAddressARB(bytes);
        }

        /*
         * macOS exposes OpenGL functions directly from the framework.
         */
        else if (isMacOS()) {
            address = NativeLibrary
                    .getInstance("OpenGL")
                    .getFunction(name)
                    .getPointer();
        }

        return address;
    }

    private static boolean loadFunction(String name) {

        Pointer address = getProcAddress(name);

        if (address == null) {
            return false;
        }

        functions.put(name, address);
        return true;
    }

    public static Pointer getAddress(String name) {
        return functions.get(name);
    }

    public static boolean hasFunction(String name) {
        return functions.containsKey(name);
    }

    /*
     * -------------------------------------------------------------------------
     * OpenGL functions
     * -------------------------------------------------------------------------
     */

    private static boolean loadCoreFunctions() {

        String[] names = {

                // OpenGL 1.1
                "glClear",
                "glClearColor",
                "glClearDepth",
                "glClearStencil",

                "glEnable",
                "glDisable",

                "glViewport",
                "glScissor",

                "glGetError",
                "glGetString",
                "glGetIntegerv",

                // Drawing
                "glBegin",
                "glEnd",

                "glVertex
