/**
 * Objective-C++ implementation of the Cocoa bridge declared in
 * MetalSurface_mac.h. Compiled only on macOS.
 */

#include "MetalSurface_mac.h"

#if defined(__APPLE__)

// The AppKit umbrella header pulls in NSWindow so `view.window`'s
// `backingScaleFactor` resolves — `<AppKit/NSView.h>` alone only
// forward-declares NSWindow.
#import <AppKit/AppKit.h>
#import <QuartzCore/CAMetalLayer.h>

void* wgpu_macos_attach_metal_layer(void* nsview_ptr) {
    if (!nsview_ptr) {
        return nullptr;
    }
    NSView* view = (__bridge NSView*)nsview_ptr;

    // When QWindow::surfaceType is QSurface::MetalSurface, Qt already
    // backs the NSView with a CAMetalLayer — just hand it back. Otherwise
    // attach one ourselves (defensive: Qt's behaviour can change between
    // major versions and 6.x has occasionally regressed this).
    CAMetalLayer* layer = nil;
    if ([view.layer isKindOfClass:[CAMetalLayer class]]) {
        layer = (CAMetalLayer*)view.layer;
    } else {
        layer = [CAMetalLayer layer];
        view.wantsLayer = YES;
        view.layer = layer;
    }

    // Track the screen's backing scale so we get retina-resolution
    // drawables. wgpu's surface configure picks the drawable size up
    // from layer.drawableSize at present-time.
    if (view.window) {
        layer.contentsScale = view.window.backingScaleFactor;
    }

    return (__bridge void*)layer;
}

#endif // __APPLE__
