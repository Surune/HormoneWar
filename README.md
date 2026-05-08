# HormoneWar

Unity migration target: `6000.4.1f1`

## Open

1. Open this folder with Unity Hub using Unity `6000.4.1f1`.
2. Let Unity reimport the project.
3. Open [Main.unity](C:/Users/seojk/HormoneWar/Assets/Scenes/Main.unity).
4. Press Play.

## Controls

- Move: `W A S D`
- Charge shot: hold left mouse button
- Fire: release left mouse button
- Start: `Space`
- Exit ending screen: `Escape`

## Notes

- The original Python/Pygame version has been migrated into a Unity UI-driven runtime.
- Scene and asset references are serialized through Unity `.meta` GUID links instead of `Resources.Load`.
- Original source assets remain in the repository root and are copied under `Assets`.
