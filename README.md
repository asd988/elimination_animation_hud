# Elimination Animation HUD

This is a minecraft resource pack that makes a valorant-like kill feedback, that appears on the HUD. It uses fonts and shaders to achieve the result. You can browse the repository if you're curious about how it works.

## Making your own animation

If you want to change it to your own animation, you can use the script I made.

Use the [`cli.py`](cli.py), you need to install python and required libraries (`requirements.txt`). See [`script_options.toml`](script_options.toml) how to use it, and how to configure it.

## Get it working

This is only a resource pack, so to actually see it in action you'll have to do that part yourself. I used Minestom, because I couldn't bother with making a datapack, but the implementation is very simple.

You would have to implement this in your own environment:

```kotlin
val animationCharacters = arrayOf(
    "\u0001",               // first elimination
    "\u0002",               // second elimination
    "\u0003",               // third elimination
    "\u0004",               // fourth elimination
    "\u0005\uffff\u1005",   // fifth elimination
)

// display the resulting component on the action bar
fun getComponent(gameTime: Long, killCount: Int): Component {
    val shaderTime: Int = ((gameTime + 1) % 24000).toInt()
    val r = shaderTime and 0xFF         // shaderTime % 256
    val g = (shaderTime shr 8) and 0xFF // shaderTime / 256

    return Component
        .text(animationCharacters[count-1])
        .font(Key.key("text_anim", "text_anim"))
        .color(TextColor.color(r, g, 123))
}
```

For datapacks the gameTime is `time query gametime`, and I'm pretty sure you have to convert the scores to hexadecimal and use macros to display it with a certain color.

I might make datapack for it later.

## My video on it

[https://youtu.be/n27M64nlHXY](https://youtu.be/n27M64nlHXY)