"""
init_db.py – Füllt die Datenbank mit umfangreichen Testdaten.

Testaccounts (alle Passwörter = Username + "123"):
  admin     / admin123   (is_admin=True)
  alice     / alice123
  bob       / bob123
  charlie   / charlie123
  diana     / diana123
  eve       / eve123
  frank     / frank123
  guest     / guest123
"""

import bcrypt
from database import Base, engine, SessionLocal
import models


# ---------------------------------------------------------------------------
# Hilfsfunktion: Klartext-Passwort → bcrypt-Hash
# ---------------------------------------------------------------------------
def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ---------------------------------------------------------------------------
# Shader-Code Snippets für die Testdaten
# ---------------------------------------------------------------------------
SHADER_RAINBOW = """\
#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

vec3 hsvToRgb(vec3 c) {
    vec3 p = abs(fract(c.xxx + vec3(0.0, 2.0/3.0, 1.0/3.0)) * 6.0 - 3.0);
    return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}

void main() {
    float hue = fract((TexCoord.x + TexCoord.y) * 0.5 + uTime * 0.15);
    outputColor = vec4(hsvToRgb(vec3(hue, 1.0, 1.0)), 1.0);
}"""

SHADER_PLASMA = """\
#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

void main() {
    vec2 uv = TexCoord * 4.0;
    float v = sin(uv.x + uTime);
    v += sin(uv.y + uTime);
    v += sin((uv.x + uv.y) + uTime);
    v += sin(sqrt(uv.x*uv.x + uv.y*uv.y + 1.0) + uTime);
    vec3 col = vec3(sin(v * 3.14159), sin(v * 3.14159 + 2.09), sin(v * 3.14159 + 4.19));
    outputColor = vec4(col * 0.5 + 0.5, 1.0);
}"""

SHADER_CHECKER = """\
#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

void main() {
    vec2 uv = floor(TexCoord * 8.0);
    float pattern = mod(uv.x + uv.y, 2.0);
    vec3 col = mix(vec3(0.1, 0.1, 0.1), vec3(0.9, 0.9, 0.9), pattern);
    outputColor = vec4(col, 1.0);
}"""

SHADER_CIRCLES = """\
#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

void main() {
    vec2 uv = TexCoord - 0.5;
    float r = length(uv);
    float rings = sin(r * 20.0 - uTime * 2.0);
    vec3 col = vec3(rings * 0.5 + 0.5, 0.2, 1.0 - rings * 0.5);
    outputColor = vec4(col, 1.0);
}"""

SHADER_NOISE = """\
#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    vec2 uv = TexCoord * 10.0;
    float n = rand(floor(uv) + floor(uTime));
    outputColor = vec4(vec3(n), 1.0);
}"""

SHADER_GRADIENT = """\
#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

void main() {
    vec3 a = vec3(0.9, 0.2, 0.4);
    vec3 b = vec3(0.1, 0.5, 0.9);
    vec3 col = mix(a, b, TexCoord.y + sin(uTime) * 0.1);
    outputColor = vec4(col, 1.0);
}"""

SHADER_WARP = """\
#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

void main() {
    vec2 uv = TexCoord;
    uv.x += sin(uv.y * 10.0 + uTime) * 0.05;
    uv.y += cos(uv.x * 10.0 + uTime) * 0.05;
    vec3 col = vec3(uv, 0.5 + 0.5 * sin(uTime));
    outputColor = vec4(col, 1.0);
}"""

SHADER_SOLID_RED = """\
#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

void main() {
    outputColor = vec4(0.85, 0.1, 0.1, 1.0);
}"""

SHADER_SCANLINES = """\
#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

void main() {
    float line = mod(TexCoord.y * 200.0, 2.0);
    float bright = step(1.0, line);
    vec3 green = vec3(0.0, bright * 0.9, 0.0);
    outputColor = vec4(green, 1.0);
}"""

SHADER_VORTEX = """\
#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

void main() {
    vec2 uv = TexCoord - 0.5;
    float angle = atan(uv.y, uv.x) + uTime;
    float r = length(uv);
    float spiral = sin(angle * 5.0 - r * 20.0);
    vec3 col = vec3(spiral * 0.5 + 0.5, r, 1.0 - r);
    outputColor = vec4(col, 1.0);
}"""


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(models.DBUsers).first() is not None:
            print("Datenbank enthält bereits Daten – Seeding wird übersprungen.")
            return

        print("Starte Seeding …")

        # ------------------------------------------------------------------ #
        # 1. USERS                                                             #
        # ------------------------------------------------------------------ #
        users_data = [
            ("admin",   "admin123",   True),
            ("alice",   "alice123",   False),
            ("bob",     "bob123",     False),
            ("charlie", "charlie123", False),
            ("diana",   "diana123",   False),
            ("eve",     "eve123",     False),
            ("frank",   "frank123",   False),
            ("guest",   "guest123",   False),
        ]

        user_objs = []
        for name, pw, is_admin in users_data:
            u = models.DBUsers(UserName=name, passwd=hash_pw(pw), is_admin=is_admin)
            db.add(u)
            user_objs.append(u)

        db.commit()
        for u in user_objs:
            db.refresh(u)

        # Kurzreferenzen
        admin, alice, bob, charlie, diana, eve, frank, guest = user_objs
        print(f"  ✓ {len(user_objs)} User angelegt")

        # ------------------------------------------------------------------ #
        # 2. TAGS                                                              #
        # ------------------------------------------------------------------ #
        tag_names = [
            "retro", "abstract", "raymarching", "procedural",
            "colorful", "minimal", "animated", "glitch",
            "psychedelic", "geometric",
        ]
        tag_objs = []
        for name in tag_names:
            t = models.DBTags(TagName=name)
            db.add(t)
            tag_objs.append(t)

        db.commit()
        for t in tag_objs:
            db.refresh(t)

        # Tag-Dict für einfachen Zugriff
        tags = {t.TagName: t for t in tag_objs}
        print(f"  ✓ {len(tag_objs)} Tags angelegt")

        # ------------------------------------------------------------------ #
        # 3. SHADERS                                                           #
        # ------------------------------------------------------------------ #
        shaders_data = [
            (alice,   "Rainbow Diagonal",  SHADER_RAINBOW,   ["colorful", "animated", "psychedelic"]),
            (alice,   "Plasma Wave",       SHADER_PLASMA,    ["psychedelic", "animated", "colorful"]),
            (bob,     "Checkerboard",      SHADER_CHECKER,   ["geometric", "minimal", "retro"]),
            (bob,     "Ripple Circles",    SHADER_CIRCLES,   ["animated", "abstract", "colorful"]),
            (charlie, "Glitch Noise",      SHADER_NOISE,     ["glitch", "retro", "abstract"]),
            (charlie, "Gradient Shift",    SHADER_GRADIENT,  ["colorful", "minimal", "animated"]),
            (diana,   "UV Warp",           SHADER_WARP,      ["abstract", "animated", "psychedelic"]),
            (diana,   "Solid Red",         SHADER_SOLID_RED, ["minimal"]),
            (eve,     "CRT Scanlines",     SHADER_SCANLINES, ["retro", "glitch", "geometric"]),
            (frank,   "Vortex Spiral",     SHADER_VORTEX,    ["psychedelic", "animated", "raymarching"]),
        ]

        shader_objs = []
        for owner, name, code, tag_list in shaders_data:
            s = models.DBShader(user_id=owner.UserId, ShaderName=name, ShaderCode=code)
            db.add(s)
            shader_objs.append((s, tag_list))

        db.commit()
        for s, _ in shader_objs:
            db.refresh(s)

        print(f"  ✓ {len(shader_objs)} Shader angelegt")

        # ------------------------------------------------------------------ #
        # 4. SHADER-TAGS                                                       #
        # ------------------------------------------------------------------ #
        # Zugriff auf Shader-Objekte ohne tag_list
        shaders = [s for s, _ in shader_objs]

        for (shader, tag_list), owner_user in zip(shader_objs, [alice, alice, bob, bob, charlie, charlie, diana, diana, eve, frank]):
            for tag_name in tag_list:
                if tag_name in tags:
                    st = models.DBShaderTags(
                        shader_id=shader.ShaderId,
                        tag_id=tags[tag_name].TagId,
                        user_id=owner_user.UserId,
                    )
                    db.add(st)

        db.commit()
        print("  ✓ ShaderTags verknüpft")

        # ------------------------------------------------------------------ #
        # 5. LIKES                                                             #
        # ------------------------------------------------------------------ #
        # Wer liked welchen Shader (shader_index, user)
        likes_data = [
            (0, bob), (0, charlie), (0, diana), (0, eve), (0, frank), (0, guest),   # Rainbow sehr beliebt
            (1, bob), (1, charlie), (1, guest),                                      # Plasma
            (2, alice), (2, eve),                                                    # Checkerboard
            (3, alice), (3, charlie), (3, frank),                                   # Ripple
            (4, alice), (4, diana),                                                  # Glitch Noise
            (5, bob), (5, eve), (5, guest),                                         # Gradient
            (6, alice), (6, bob), (6, charlie),                                     # Warp
            (7, charlie),                                                            # Solid Red (wenig Likes)
            (8, alice), (8, bob), (8, diana), (8, frank),                           # Scanlines
            (9, alice), (9, bob), (9, charlie), (9, diana), (9, eve), (9, guest),  # Vortex sehr beliebt
        ]

        for shader_idx, liker in likes_data:
            like = models.DBLikes(shader_id=shaders[shader_idx].ShaderId, user_id=liker.UserId)
            db.add(like)

        db.commit()
        print(f"  ✓ {len(likes_data)} Likes angelegt")

        # ------------------------------------------------------------------ #
        # 6. COMMENTS                                                          #
        # ------------------------------------------------------------------ #
        comments_data = [
            # (shader_idx, author_user, text)
            (0, bob,     "Absolut atemberaubend! Die Farben sind perfekt."),
            (0, charlie, "Erinnert mich an alte Demoscene-Intros!"),
            (0, diana,   "Wie hast du den HSV-Übergang so smooth hingekriegt?"),
            (0, eve,     "Mein neuer Lieblingsshader. 10/10"),
            (1, alice,   "Die Plasma-Welle sieht hypnotisch aus."),
            (1, charlie, "Klassischer Plasma-Effekt, super umgesetzt!"),
            (2, alice,   "Schön minimalistisch. Gefällt mir."),
            (2, eve,     "Könnte man noch animieren – würde gut aussehen."),
            (3, frank,   "Die Ringe erinnern mich an Wassertropfen."),
            (3, diana,   "Sehr flüssige Animation!"),
            (4, diana,   "Der Glitch-Effekt ist so authentisch."),
            (5, bob,     "Super subtiler Gradient. Nicht zu viel, nicht zu wenig."),
            (5, guest,   "Für Hintergrundgrafiken perfekt."),
            (6, alice,   "Der Warp-Effekt macht mich schwindlig – im guten Sinne!"),
            (6, charlie, "Wie eine Hitzewelle über Asphalt."),
            (8, alice,   "CRT-Nostalgie pur!"),
            (8, frank,   "Brauche das als Screensaver."),
            (8, diana,   "Kombinier das mal mit einem Scan-Noise."),
            (9, alice,   "Der Vortex saugt mich rein. Fantastisch."),
            (9, charlie, "Bitte mach eine Version mit mehr Spiralarmen!"),
            (9, eve,     "Das ist ein echter Hingucker."),
            (9, diana,   "Top-Shader, verdient mehr Likes!"),
        ]

        for shader_idx, author, text in comments_data:
            c = models.DBComments(
                CommentText=text,
                CommentAuthor=author.UserName,
                user_id=author.UserId,
                shader_id=shaders[shader_idx].ShaderId,
            )
            db.add(c)

        db.commit()
        print(f"  ✓ {len(comments_data)} Kommentare angelegt")

        # ------------------------------------------------------------------ #
        # 7. LOGGING                                                           #
        # ------------------------------------------------------------------ #
        log_entries = [
            (admin.UserId,   "Admin-Account erstellt."),
            (alice.UserId,   "User alice hat sich eingeloggt."),
            (alice.UserId,   "User alice hat Shader 'Rainbow Diagonal' erstellt."),
            (bob.UserId,     "User bob hat sich eingeloggt."),
            (charlie.UserId, "User charlie hat Shader 'Glitch Noise' hochgeladen."),
            (admin.UserId,   "Admin hat Benutzerliste abgerufen."),
            (diana.UserId,   "User diana hat ihr Passwort geändert."),
            (eve.UserId,     "User eve hat Shader 9 geliked."),
        ]

        for uid, text in log_entries:
            log = models.DBLogging(user_id=uid, LogText=text)
            db.add(log)

        db.commit()
        print(f"  ✓ {len(log_entries)} Log-Einträge angelegt")

        # ------------------------------------------------------------------ #
        # Zusammenfassung                                                       #
        # ------------------------------------------------------------------ #
        print("\n✅ Seeding abgeschlossen!")
        print("─" * 45)
        print(f"  Users:      {len(user_objs)}")
        print(f"  Tags:       {len(tag_objs)}")
        print(f"  Shaders:    {len(shaders)}")
        print(f"  Likes:      {len(likes_data)}")
        print(f"  Kommentare: {len(comments_data)}")
        print(f"  Logs:       {len(log_entries)}")
        print("─" * 45)
        print("\nTestaccounts (Passwort = Username + '123'):")
        for name, pw, is_admin in users_data:
            role = "ADMIN" if is_admin else "User "
            print(f"  [{role}]  {name:<10} / {pw}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seeding fehlgeschlagen, Rollback: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()