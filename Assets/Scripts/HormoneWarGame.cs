using System;
using System;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public sealed class HormoneWarGame : MonoBehaviour
{
    private const float ReferenceWidth = 640f;
    private const float ReferenceHeight = 640f;
    private const float FrameRate = 30f;
    private const float MaxHealth = 8401f;
    private const float MaxSpeed = 1f;
    private const float ChargeTerm = 20f;
    private const float ShotGap = 15f;
    private const float InvisibleTime = 20f;
    private const float HormoneSpawnTime = 150f;
    private const float HormoneLastTime = 200f;

    private static readonly Color BossOrange = ParseColor("#FF7F27");
    private static readonly Color BossViolet = ParseColor("#A34CAD");
    private static readonly Color TileGreen = ParseColor("#2C8A4E");

    private readonly HormoneDefinition[] hormoneDefinitions =
    {
        new HormoneDefinition("Epinephrine", 1f, 1f, 1f, 0),
        new HormoneDefinition("Melatonin", -1f, -1f, -1f, 2),
        new HormoneDefinition("Growth Hormone", 0f, 2f, 0f, 1),
        new HormoneDefinition("Serotonin", -1f, 1f, 2f, 0),
        new HormoneDefinition("Dopamine", 5f, 0f, 0f, 0),
        new HormoneDefinition("Oxytocin", 1f, 0f, 1f, 0),
        new HormoneDefinition("Endorphin", 0f, 1f, 1f, 1),
        new HormoneDefinition("Insulin", 1f, 0f, 2f, 0),
        new HormoneDefinition("Glucagon", 2f, 0f, -1f, 0),
        new HormoneDefinition("Cortisol", 3f, -1f, 0f, 0),
    };

    private readonly List<ProjectileState> playerShots = new();
    private readonly List<ProjectileState> enemyShots = new();
    private readonly List<HormoneEffect> activeHormones = new();
    private readonly List<Image> hearts = new();

    private readonly Color[] bossPhaseColors =
    {
        Color.red,
        BossOrange,
        Color.yellow,
        Color.green,
        Color.blue,
        BossViolet,
    };

    private readonly Vector2[] shot4Offsets =
    {
        Vector2.up * -41f + Vector2.right * 3f,
        Vector2.up * -32f + Vector2.right * 6f,
        Vector2.up * -23f + Vector2.right * 9f,
        Vector2.up * -14f + Vector2.right * 12f,
        Vector2.up * -5f + Vector2.right * 15f,
        Vector2.up * -10.6f + Vector2.right * 7f,
        Vector2.up * -16.2f + Vector2.right * -1f,
        Vector2.up * -21.8f + Vector2.right * -9f,
        Vector2.up * -27.4f + Vector2.right * -17f,
        Vector2.up * -33f + Vector2.right * -25f,
        Vector2.up * -33f + Vector2.right * -15.1f,
        Vector2.up * -33f + Vector2.right * -5.2f,
        Vector2.up * -33f + Vector2.right * 4.7f,
        Vector2.up * -33f + Vector2.right * 14.6f,
        Vector2.up * -33f + Vector2.right * 24.5f,
        Vector2.up * -27.4f + Vector2.right * 16.5f,
        Vector2.up * -21.8f + Vector2.right * 8.5f,
        Vector2.up * -16.2f + Vector2.right * 0.5f,
        Vector2.up * -10.6f + Vector2.right * -7.5f,
        Vector2.up * -5f + Vector2.right * -15.5f,
        Vector2.up * -14f + Vector2.right * -12.5f,
        Vector2.up * -23f + Vector2.right * -9.5f,
        Vector2.up * -32f + Vector2.right * -6.5f,
        Vector2.up * -41f + Vector2.right * -3.5f,
        Vector2.up * -50f + Vector2.right * -0.5f,
    };

    private readonly System.Random random = new();

    [SerializeField] private AssetSources assetSources = new AssetSources();

    private AssetBank assets;
    private RectTransform canvasRect;
    private CanvasGroup menuGroup;
    private CanvasGroup missionGroup;
    private CanvasGroup endingGroup;
    private CanvasGroup battleGroup;
    private Image endingImage;
    private Image cursorImage;
    private Image playerImage;
    private Image buffImage;
    private Image enemyImage;
    private Image enemyHealthBack;
    private Image enemyHealthFill;
    private Image hormonePickupImage;
    private Image hormoneDurationFill;
    private TMP_Text hormoneLabel;
    private RectTransform playerRect;
    private RectTransform enemyRect;
    private RectTransform cursorRect;
    private RectTransform hormoneRect;
    private RectTransform playerShotRoot;
    private RectTransform enemyShotRoot;
    private RectTransform heartRoot;
    private AudioSource musicSource;

    private GameState state;
    private PlayerState player;
    private EnemyState enemy;
    private HormonePickupState pickup;
    private float missionTimer;
    private float endingTimer;

    private void Awake()
    {
        Screen.SetResolution((int)ReferenceWidth, (int)ReferenceHeight, false);
        Application.targetFrameRate = 60;
        Cursor.visible = false;
        assets = new AssetBank(assetSources);
        gameObject.AddComponent<AudioListener>();
        musicSource = gameObject.AddComponent<AudioSource>();
        BuildEventSystem();
        BuildCanvas();
        BuildBattleLayer();
        BuildOverlayLayer();
        StartMenu();
    }

    private void Update()
    {
        UpdateCursor();

        if (state == GameState.Menu)
        {
            if (Input.GetKeyDown(KeyCode.Space))
            {
                StartMission();
            }

            return;
        }

        if (state == GameState.Mission)
        {
            missionTimer -= Time.unscaledDeltaTime;
            if (missionTimer <= 0f)
            {
                StartBattle();
            }

            return;
        }

        if (state == GameState.Ending)
        {
            endingTimer += Time.unscaledDeltaTime;
            if (endingTimer > 0.1f && Input.GetKeyDown(KeyCode.Escape))
            {
                SceneManager.LoadScene(SceneManager.GetActiveScene().path);
            }

            return;
        }

        UpdateBattle();
    }

    private void BuildEventSystem()
    {
        var system = new GameObject("EventSystem");
        system.AddComponent<EventSystem>();
        system.AddComponent<StandaloneInputModule>();
    }

    private void BuildCanvas()
    {
        var canvasObject = new GameObject("Canvas");
        canvasObject.transform.SetParent(transform, false);

        var canvas = canvasObject.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.pixelPerfect = true;

        canvasObject.AddComponent<GraphicRaycaster>();

        var scaler = canvasObject.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = Vector2.right * ReferenceWidth + Vector2.up * ReferenceHeight;
        scaler.matchWidthOrHeight = 0.5f;

        canvasRect = canvasObject.GetComponent<RectTransform>();
        canvasRect.anchorMin = Vector2.zero;
        canvasRect.anchorMax = Vector2.one;
        canvasRect.offsetMin = Vector2.zero;
        canvasRect.offsetMax = Vector2.zero;
    }

    private void BuildBattleLayer()
    {
        battleGroup = CreateGroup("Battle", canvasRect);
        battleGroup.alpha = 0f;
        battleGroup.interactable = false;
        battleGroup.blocksRaycasts = false;

        var tileRoot = CreateRect("Tiles", battleGroup.transform as RectTransform);
        tileRoot.anchorMin = Vector2.zero;
        tileRoot.anchorMax = Vector2.one;
        tileRoot.offsetMin = Vector2.zero;
        tileRoot.offsetMax = Vector2.zero;

        var tileWidth = assets.TileGreen.rect.width;
        var tileHeight = assets.TileGreen.rect.height;
        var columns = Mathf.CeilToInt(ReferenceWidth / tileWidth);
        var rows = Mathf.CeilToInt(ReferenceHeight / tileHeight);

        for (var y = 0; y < rows; y++)
        {
            for (var x = 0; x < columns; x++)
            {
                var tile = CreateImage("Tile", tileRoot, assets.TileGreen);
                SetCenteredSize(tile.rectTransform, tileWidth, tileHeight);
                tile.rectTransform.anchoredPosition =
                    Vector2.right * (-ReferenceWidth * 0.5f + tileWidth * 0.5f + tileWidth * x) +
                    Vector2.up * (-ReferenceHeight * 0.5f + tileHeight * 0.5f + tileHeight * y);
                tile.color = TileGreen;
            }
        }

        playerShotRoot = CreateRect("PlayerShots", battleGroup.transform as RectTransform);
        enemyShotRoot = CreateRect("EnemyShots", battleGroup.transform as RectTransform);

        buffImage = CreateImage("Buff", battleGroup.transform as RectTransform, assets.Buff);
        buffImage.enabled = false;

        hormonePickupImage = CreateImage("HormonePickup", battleGroup.transform as RectTransform, assets.Hormones[0]);
        hormonePickupImage.enabled = false;
        hormoneRect = hormonePickupImage.rectTransform;
        SetCenteredSize(hormoneRect, hormonePickupImage.sprite.rect.width, hormonePickupImage.sprite.rect.height);

        playerImage = CreateImage("Player", battleGroup.transform as RectTransform, assets.PlayerStandingRight);
        playerRect = playerImage.rectTransform;
        SetCenteredSize(playerRect, playerImage.sprite.rect.width, playerImage.sprite.rect.height);

        enemyImage = CreateImage("Enemy", battleGroup.transform as RectTransform, assets.EnemyIdle);
        enemyRect = enemyImage.rectTransform;
        SetCenteredSize(enemyRect, enemyImage.sprite.rect.width, enemyImage.sprite.rect.height);

        enemyHealthBack = CreateImage("EnemyHealthBack", battleGroup.transform as RectTransform, assets.White);
        enemyHealthBack.color = Color.white;
        SetCenteredSize(enemyHealthBack.rectTransform, 140f, 7f);

        enemyHealthFill = CreateImage("EnemyHealthFill", battleGroup.transform as RectTransform, assets.White);
        enemyHealthFill.color = Color.red;
        SetCenteredSize(enemyHealthFill.rectTransform, 140f, 7f);

        hormoneDurationFill = CreateImage("HormoneFill", battleGroup.transform as RectTransform, assets.White);
        hormoneDurationFill.color = Color.red;
        SetCenteredSize(hormoneDurationFill.rectTransform, 40f, 3f);
        hormoneDurationFill.enabled = false;

        hormoneLabel = CreateText("HormoneLabel", battleGroup.transform as RectTransform, 20f);
        hormoneLabel.alignment = TextAlignmentOptions.Center;
        hormoneLabel.gameObject.SetActive(false);

        heartRoot = CreateRect("Hearts", battleGroup.transform as RectTransform);

        cursorImage = CreateImage("Cursor", canvasRect, assets.Cursor);
        cursorRect = cursorImage.rectTransform;
        SetCenteredSize(cursorRect, cursorImage.sprite.rect.width, cursorImage.sprite.rect.height);
    }

    private void BuildOverlayLayer()
    {
        menuGroup = CreateFullscreenGroup("Menu", assets.Menu);
        missionGroup = CreateFullscreenGroup("Mission", assets.Mission);
        endingGroup = CreateFullscreenGroup("Ending", assets.GameOver);
        endingImage = endingGroup.GetComponentInChildren<Image>();
    }

    private CanvasGroup CreateFullscreenGroup(string name, Sprite sprite)
    {
        var group = CreateGroup(name, canvasRect);
        var image = CreateImage(name + "Image", group.transform as RectTransform, sprite);
        image.rectTransform.anchorMin = Vector2.zero;
        image.rectTransform.anchorMax = Vector2.one;
        image.rectTransform.offsetMin = Vector2.zero;
        image.rectTransform.offsetMax = Vector2.zero;
        image.preserveAspect = false;
        return group;
    }

    private void StartMenu()
    {
        state = GameState.Menu;
        SetGroupVisible(menuGroup, true);
        SetGroupVisible(missionGroup, false);
        SetGroupVisible(endingGroup, false);
        SetGroupVisible(battleGroup, false);
        PlayMusic(assets.MenuMusic);
        ClearDynamicObjects();
    }

    private void StartMission()
    {
        state = GameState.Mission;
        missionTimer = 50f / FrameRate;
        SetGroupVisible(menuGroup, false);
        SetGroupVisible(missionGroup, true);
        SetGroupVisible(endingGroup, false);
        SetGroupVisible(battleGroup, false);
    }

    private void StartBattle()
    {
        state = GameState.Battle;
        SetGroupVisible(menuGroup, false);
        SetGroupVisible(missionGroup, false);
        SetGroupVisible(endingGroup, false);
        SetGroupVisible(battleGroup, true);
        PlayMusic(assets.GameMusic);
        ResetBattleState();
    }

    private void FinishBattle(bool win)
    {
        state = GameState.Ending;
        endingTimer = 0f;
        endingImage.sprite = win ? assets.YouWin : assets.GameOver;
        SetGroupVisible(menuGroup, false);
        SetGroupVisible(missionGroup, false);
        SetGroupVisible(endingGroup, true);
        SetGroupVisible(battleGroup, false);
        PlayMusic(assets.EndingMusic);
    }

    private void ResetBattleState()
    {
        ClearDynamicObjects();

        player = new PlayerState
        {
            speed = MaxSpeed,
            damage = 15f,
            life = 5,
            x = ReferenceWidth * 0.5f,
            y = ReferenceHeight * 0.5f,
            shotSpeed = 10f,
            directionRight = true,
        };

        enemy = new EnemyState
        {
            health = MaxHealth,
            x = RandomRange(25f, ReferenceWidth - 60f),
            y = RandomRange(25f, ReferenceHeight - 60f),
            level = 4,
            shotSpeed = 19f,
            choice = random.Next(1, 5),
            phaseSprite = assets.EnemyIdle,
        };

        pickup = new HormonePickupState
        {
            cooldown = 0f,
            hormoneIndex = 0,
            x = 0f,
            y = 0f,
        };

        RollNextHormone();
        RefreshHearts();
        UpdatePlayerSprite();
        UpdateEnemySprite();
        UpdateEnemyHealthBar();
        UpdateActorPositions();
    }

    private void UpdateBattle()
    {
        var frameDelta = Time.unscaledDeltaTime * FrameRate;
        UpdatePlayer(frameDelta);
        UpdateHormoneSpawn(frameDelta);
        UpdatePlayerShots(frameDelta);
        UpdateEnemyAttack(frameDelta);
        UpdateEnemyShots(frameDelta);
        UpdateHormoneEffects(frameDelta);
        UpdateEnemyHealthBar();
        UpdateActorPositions();
        RefreshHearts();

        if (player.life <= 0)
        {
            FinishBattle(false);
            return;
        }

        if (enemy.health <= 0f)
        {
            FinishBattle(true);
        }
    }

    private void UpdatePlayer(float frameDelta)
    {
        player.shotCooldown -= frameDelta;
        player.invisibleCooldown -= frameDelta;
        if (player.invisibleCooldown <= 0f)
        {
            player.invisible = false;
        }

        if (Input.GetKey(KeyCode.A))
        {
            player.directionRight = false;
            player.runIndex = (player.runIndex + 1) % assets.PlayerRunRight.Length;
            player.x = Mathf.Clamp(player.x - player.speed * frameDelta, 10f, ReferenceWidth - 15f);
        }

        if (Input.GetKey(KeyCode.D))
        {
            player.directionRight = true;
            player.runIndex = (player.runIndex + 1) % assets.PlayerRunRight.Length;
            player.x = Mathf.Clamp(player.x + player.speed * frameDelta, 10f, ReferenceWidth - 15f);
        }

        if (Input.GetKey(KeyCode.W))
        {
            player.y = Mathf.Clamp(player.y + player.speed * frameDelta, 10f, ReferenceHeight - 15f);
        }

        if (Input.GetKey(KeyCode.S))
        {
            player.y = Mathf.Clamp(player.y - player.speed * frameDelta, 10f, ReferenceHeight - 15f);
        }

        if (Input.GetMouseButtonDown(0) && player.shotCooldown <= 0f && !player.charging)
        {
            player.charging = true;
        }

        if (player.charging)
        {
            player.chargingTime += frameDelta;
            player.speed = 0f;
            player.chargeLevel = Mathf.Min(Mathf.FloorToInt(player.chargingTime / ChargeTerm), 3);
        }
        else
        {
            player.speed = MaxSpeed;
            player.chargingTime = 0f;
            player.chargeLevel = 0;
        }

        if (Input.GetMouseButtonUp(0) && player.charging)
        {
            FirePlayerShot();
        }

        UpdatePlayerSprite();
    }

    private void FirePlayerShot()
    {
        var mouse = Input.mousePosition;
        var mouseX = mouse.x * ReferenceWidth / Screen.width;
        var mouseY = mouse.y * ReferenceHeight / Screen.height;
        var theta = Mathf.PI * 0.5f - Mathf.Atan2(mouseY - player.y + 5f, mouseX - player.x - 10f);

        playerShots.Add(new ProjectileState
        {
            x = player.x - 10f,
            y = player.y + 5f,
            theta = theta,
            level = player.chargeLevel,
            image = CreateImage("PlayerShot", playerShotRoot, assets.PlayerShots[player.chargeLevel]),
            speed = player.shotSpeed,
        });

        var created = playerShots[playerShots.Count - 1];
        SetCenteredSize(created.image.rectTransform, created.image.sprite.rect.width, created.image.sprite.rect.height);
        player.charging = false;
        player.chargingTime = 0f;
        player.speed = MaxSpeed;
        player.shotCooldown = ShotGap;
    }

    private void UpdatePlayerShots(float frameDelta)
    {
        for (var index = playerShots.Count - 1; index >= 0; index--)
        {
            var shot = playerShots[index];
            shot.x += shot.speed * Mathf.Sin(shot.theta) * frameDelta;
            shot.y += shot.speed * Mathf.Cos(shot.theta) * frameDelta;

            if (shot.x < 0f || shot.y < 0f || shot.x > ReferenceWidth || shot.y > ReferenceHeight)
            {
                Destroy(shot.image.gameObject);
                playerShots.RemoveAt(index);
                continue;
            }

            if (Mathf.Abs(shot.x - enemy.x) <= enemyImage.sprite.rect.width * 0.5f &&
                Mathf.Abs(shot.y - enemy.y) <= enemyImage.sprite.rect.height * 0.5f)
            {
                enemy.health -= player.damage;
                Destroy(shot.image.gameObject);
                playerShots.RemoveAt(index);
                continue;
            }

            shot.image.rectTransform.anchoredPosition = ScreenToCanvas(shot.x, shot.y);
            shot.image.rectTransform.localRotation = Quaternion.Euler(0f, 0f, 90f + shot.theta * Mathf.Rad2Deg);
        }
    }

    private void UpdateEnemyAttack(float frameDelta)
    {
        enemy.attackFrame += frameDelta;
        if (enemy.attackFrame < 30f)
        {
            enemy.phaseSprite = assets.EnemyIdle;
            UpdateEnemySprite();
            return;
        }

        if (enemy.attackFrame < 35f)
        {
            enemy.phaseSprite = enemy.choice == 5 ? assets.EnemyReady : assets.EnemyCharge;
            UpdateEnemySprite();
            return;
        }

        enemy.phaseSprite = assets.EnemyShoot;
        UpdateEnemySprite();

        if (enemy.choice == 1)
        {
            UpdatePattern1(frameDelta);
            return;
        }

        if (enemy.choice == 2)
        {
            UpdatePattern2(frameDelta);
            return;
        }

        if (enemy.choice == 3)
        {
            UpdatePattern3(frameDelta);
            return;
        }

        if (enemy.choice == 4)
        {
            UpdatePattern4(frameDelta);
            return;
        }

        TeleportEnemy();
    }

    private void UpdatePattern1(float frameDelta)
    {
        var before = enemy.patternFrame;
        AdvancePatternFrame(frameDelta);
        var beforeStep = Mathf.FloorToInt(before);
        var afterStep = Mathf.FloorToInt(enemy.patternFrame);

        for (var step = beforeStep + 1; step <= afterStep; step++)
        {
            if (step is >= 1 and <= 5 || step is >= 14 and <= 18 || step is >= 27 and <= 31)
            {
                SpawnPattern1Volley();
            }
        }

        if (enemy.patternFrame > 31f)
        {
            ResetAttackCycle();
        }
    }

    private void UpdatePattern2(float frameDelta)
    {
        var before = enemy.patternFrame;
        AdvancePatternFrame(frameDelta);
        var beforeStep = Mathf.FloorToInt(before);
        var afterStep = Mathf.FloorToInt(enemy.patternFrame);

        for (var step = beforeStep + 1; step <= afterStep; step++)
        {
            if (step is >= 1 and <= 4 || step is >= 8 and <= 10 || step is >= 14 and <= 16 || step is >= 20 and <= 22)
            {
                SpawnPattern2Volley();
            }

            if (step is 5 or 6 or 11 or 12 or 17 or 18)
            {
                enemy.tempTheta = Mathf.Atan2(player.x - enemy.x, player.y - enemy.y);
            }
        }

        if (enemy.patternFrame < 23f)
        {
            return;
        }

        enemy.tempTheta = 0f;
        ResetAttackCycle();
    }

    private void UpdatePattern3(float frameDelta)
    {
        var before = enemy.patternFrame;
        AdvancePatternFrame(frameDelta);
        var crossed = Mathf.FloorToInt(enemy.patternFrame / 3f) - Mathf.FloorToInt(before / 3f);
        for (var index = 0; index < crossed; index++)
        {
            SpawnPattern3Volley();
        }

        if (enemy.patternFrame >= 90f)
        {
            ResetAttackCycle();
        }
    }

    private void UpdatePattern4(float frameDelta)
    {
        var before = enemy.patternFrame;
        AdvancePatternFrame(frameDelta);
        var crossed = Mathf.FloorToInt(enemy.patternFrame / 7f) - Mathf.FloorToInt(before / 7f);
        for (var index = 0; index < crossed; index++)
        {
            SpawnPattern4Volley();
        }

        if (enemy.patternFrame > 49f)
        {
            ResetAttackCycle();
        }
    }

    private void AdvancePatternFrame(float frameDelta)
    {
        enemy.patternAccumulator += frameDelta;
        while (enemy.patternAccumulator >= 1f)
        {
            enemy.patternAccumulator -= 1f;
            enemy.patternFrame += 1f;
        }
    }

    private void SpawnPattern1Volley()
    {
        for (var index = 0; index < 15; index++)
        {
            var theta = Mathf.PI * 5f * enemy.spiralIndex / 360f + (float)random.NextDouble() / 9f;
            var x = enemy.x + RandomRange(-5f, 5f);
            var y = enemy.y + RandomRange(-5f, 5f);
            SpawnEnemyShot(x, y, theta, 1, 0f);
            enemy.spiralIndex += 30;
        }
    }

    private void SpawnPattern2Volley()
    {
        for (var index = 0; index < 15; index++)
        {
            var theta = (float)random.NextDouble() / 3f;
            var x = enemy.x + RandomRange(-25f, 25f);
            var y = enemy.y + RandomRange(-25f, 25f);
            SpawnEnemyShot(x, y, enemy.tempTheta + theta, 2, 0f);
            enemy.tempTheta += 1.256f;
        }
    }

    private void SpawnPattern3Volley()
    {
        var theta = Mathf.Atan2(player.x - enemy.x, player.y - enemy.y);
        for (var index = 0; index < 16; index++)
        {
            SpawnEnemyShot(enemy.x, enemy.y, theta, 3, 0f);
            theta += Mathf.PI / 8f;
        }
    }

    private void SpawnPattern4Volley()
    {
        for (var index = 0; index < shot4Offsets.Length; index++)
        {
            var offset = shot4Offsets[index];
            var x = enemy.x + offset.x;
            var y = enemy.y + offset.y;
            var theta = Mathf.Atan2(player.x - x, player.y - y);
            SpawnEnemyShot(x, y, theta, 4, 20f);
        }
    }

    private void SpawnEnemyShot(float x, float y, float theta, int pattern, float holdFrames)
    {
        var image = CreateImage("EnemyShot", enemyShotRoot, assets.EnemyShot);
        SetCenteredSize(image.rectTransform, image.sprite.rect.width, image.sprite.rect.height);
        enemyShots.Add(new ProjectileState
        {
            x = x,
            y = y,
            theta = theta,
            pattern = pattern,
            holdFrames = holdFrames,
            image = image,
            speed = enemy.shotSpeed,
        });
    }

    private void TeleportEnemy()
    {
        enemy.phaseSprite = assets.EnemyTeleport;
        UpdateEnemySprite();
        enemy.attackFrame = 0f;
        enemy.patternFrame = 0f;
        enemy.patternAccumulator = 0f;
        enemy.choice = random.Next(1, enemy.level + 1);
        enemy.x = RandomRange(20f, ReferenceWidth - 50f);
        enemy.y = RandomRange(20f, ReferenceHeight - 50f);
    }

    private void ResetAttackCycle()
    {
        enemy.phaseSprite = assets.EnemyIdle;
        enemy.attackFrame = 0f;
        enemy.patternFrame = 0f;
        enemy.patternAccumulator = 0f;
        enemy.choice = 5;
        UpdateEnemySprite();
    }

    private void UpdateEnemyShots(float frameDelta)
    {
        for (var index = enemyShots.Count - 1; index >= 0; index--)
        {
            var shot = enemyShots[index];
            if (shot.holdFrames > 0f)
            {
                shot.holdFrames -= frameDelta;
                shot.image.rectTransform.anchoredPosition = ScreenToCanvas(shot.x, shot.y);
                continue;
            }

            shot.x += shot.speed * Mathf.Sin(shot.theta) * frameDelta;
            shot.y += shot.speed * Mathf.Cos(shot.theta) * frameDelta;

            if (shot.x < 0f || shot.y < 0f || shot.x > ReferenceWidth || shot.y > ReferenceHeight)
            {
                Destroy(shot.image.gameObject);
                enemyShots.RemoveAt(index);
                continue;
            }

            if (!player.invisible &&
                Mathf.Abs(shot.x - player.x) <= playerImage.sprite.rect.width * 0.5f &&
                Mathf.Abs(shot.y - player.y) <= playerImage.sprite.rect.height * 0.5f)
            {
                player.invisible = true;
                player.invisibleCooldown = InvisibleTime;
                player.life -= 1;
                Destroy(shot.image.gameObject);
                enemyShots.RemoveAt(index);
                continue;
            }

            shot.image.rectTransform.anchoredPosition = ScreenToCanvas(shot.x, shot.y);
        }
    }

    private void UpdateHormoneSpawn(float frameDelta)
    {
        pickup.cooldown += frameDelta;
        if (pickup.cooldown < HormoneSpawnTime)
        {
            hormonePickupImage.enabled = false;
            return;
        }

        hormonePickupImage.enabled = true;
        hormonePickupImage.sprite = assets.Hormones[pickup.hormoneIndex];
        SetCenteredSize(hormoneRect, hormonePickupImage.sprite.rect.width, hormonePickupImage.sprite.rect.height);
        hormoneRect.anchoredPosition = ScreenToCanvas(pickup.x, pickup.y);

        if (Mathf.Abs(player.x - pickup.x) <= hormonePickupImage.sprite.rect.width * 0.5f &&
            Mathf.Abs(player.y - pickup.y) <= hormonePickupImage.sprite.rect.height * 0.5f)
        {
            ApplyHormone();
        }
    }

    private void ApplyHormone()
    {
        var data = hormoneDefinitions[pickup.hormoneIndex];
        activeHormones.Add(new HormoneEffect
        {
            hormoneIndex = pickup.hormoneIndex,
            remaining = HormoneLastTime,
        });

        player.damage += data.damage;
        player.speed += data.speed;
        player.shotSpeed += data.shotSpeed;
        player.life += data.life;
        pickup.cooldown = 0f;
        RollNextHormone();
    }

    private void UpdateHormoneEffects(float frameDelta)
    {
        if (activeHormones.Count == 0)
        {
            buffImage.enabled = false;
            hormoneDurationFill.enabled = false;
            hormoneLabel.gameObject.SetActive(false);
            return;
        }

        for (var index = activeHormones.Count - 1; index >= 0; index--)
        {
            activeHormones[index].remaining -= frameDelta;
            if (activeHormones[index].remaining > 0f)
            {
                continue;
            }

            var expired = activeHormones[index];
            var data = hormoneDefinitions[expired.hormoneIndex];
            player.damage -= data.damage;
            player.speed -= data.speed;
            player.shotSpeed -= data.shotSpeed;
            activeHormones.RemoveAt(index);
        }

        if (activeHormones.Count == 0)
        {
            buffImage.enabled = false;
            hormoneDurationFill.enabled = false;
            hormoneLabel.gameObject.SetActive(false);
            return;
        }

        var current = activeHormones[activeHormones.Count - 1];
        var definition = hormoneDefinitions[current.hormoneIndex];
        buffImage.enabled = true;
        buffImage.rectTransform.anchoredPosition = ScreenToCanvas(player.x, player.y);
        buffImage.rectTransform.localScale = Vector3.one;
        hormoneDurationFill.enabled = true;
        hormoneDurationFill.rectTransform.anchoredPosition = ScreenToCanvas(player.x, player.y + 30f);
        hormoneDurationFill.rectTransform.sizeDelta = Vector2.right * (40f * current.remaining / HormoneLastTime) + Vector2.up * 3f;
        hormoneLabel.gameObject.SetActive(true);
        hormoneLabel.rectTransform.anchoredPosition = ScreenToCanvas(player.x, player.y + 45f);
        hormoneLabel.text = definition.name;
    }

    private void RollNextHormone()
    {
        pickup.hormoneIndex = random.Next(0, hormoneDefinitions.Length);
        pickup.x = RandomRange(15f, ReferenceWidth - 40f);
        pickup.y = RandomRange(15f, ReferenceHeight - 40f);
    }

    private void UpdateEnemyHealthBar()
    {
        var normalized = Mathf.Clamp01(enemy.health / MaxHealth);
        enemyHealthFill.rectTransform.sizeDelta = Vector2.right * (140f * normalized) + Vector2.up * 7f;
        var phase = Mathf.Clamp(Mathf.FloorToInt((enemy.health / 1400f) - 0.001f), 0, bossPhaseColors.Length - 1);
        enemyHealthFill.color = bossPhaseColors[phase];
        enemyHealthBack.rectTransform.anchoredPosition = ScreenToCanvas(enemy.x, enemy.y + 40f);
        enemyHealthFill.rectTransform.anchoredPosition = ScreenToCanvas(enemy.x, enemy.y + 40f);
    }

    private void UpdateActorPositions()
    {
        playerRect.anchoredPosition = ScreenToCanvas(player.x, player.y);
        enemyRect.anchoredPosition = ScreenToCanvas(enemy.x, enemy.y);
        enemyHealthFill.rectTransform.anchoredPosition = ScreenToCanvas(enemy.x, enemy.y + 40f);
    }

    private void RefreshHearts()
    {
        while (hearts.Count < player.life)
        {
            var heart = CreateImage("Heart", heartRoot, assets.Heart);
            SetCenteredSize(heart.rectTransform, heart.sprite.rect.width, heart.sprite.rect.height);
            hearts.Add(heart);
        }

        while (hearts.Count > player.life)
        {
            Destroy(hearts[hearts.Count - 1].gameObject);
            hearts.RemoveAt(hearts.Count - 1);
        }

        for (var index = 0; index < hearts.Count; index++)
        {
            hearts[index].rectTransform.anchorMin = Vector2.up;
            hearts[index].rectTransform.anchorMax = Vector2.up;
            hearts[index].rectTransform.pivot = Vector2.up * 0.5f;
            hearts[index].rectTransform.anchoredPosition =
                Vector2.right * (20f + 3f * (index + 1) + hearts[index].sprite.rect.width * index) +
                Vector2.up * -20f;
        }
    }

    private void UpdatePlayerSprite()
    {
        if (player.charging)
        {
            playerImage.sprite = player.directionRight
                ? assets.PlayerChargeRight[player.chargeLevel]
                : assets.PlayerChargeLeft[player.chargeLevel];
        }
        else if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.D))
        {
            playerImage.sprite = player.directionRight
                ? assets.PlayerRunRight[player.runIndex]
                : assets.PlayerRunLeft[player.runIndex];
        }
        else
        {
            playerImage.sprite = player.directionRight ? assets.PlayerStandingRight : assets.PlayerStandingLeft;
        }

        SetCenteredSize(playerRect, playerImage.sprite.rect.width, playerImage.sprite.rect.height);
        playerImage.enabled = !player.invisible || Mathf.FloorToInt(player.invisibleCooldown) % 2 == 0;
    }

    private void UpdateEnemySprite()
    {
        enemyImage.sprite = enemy.phaseSprite;
        SetCenteredSize(enemyRect, enemyImage.sprite.rect.width, enemyImage.sprite.rect.height);
    }

    private void UpdateCursor()
    {
        var mouse = Input.mousePosition;
        cursorRect.anchorMin = Vector2.zero;
        cursorRect.anchorMax = Vector2.zero;
        cursorRect.pivot = Vector2.one * 0.5f;
        cursorRect.anchoredPosition =
            Vector2.right * (mouse.x * ReferenceWidth / Screen.width - ReferenceWidth * 0.5f) +
            Vector2.up * (mouse.y * ReferenceHeight / Screen.height - ReferenceHeight * 0.5f);
    }

    private void ClearDynamicObjects()
    {
        foreach (var shot in playerShots)
        {
            Destroy(shot.image.gameObject);
        }

        foreach (var shot in enemyShots)
        {
            Destroy(shot.image.gameObject);
        }

        foreach (var heart in hearts)
        {
            Destroy(heart.gameObject);
        }

        playerShots.Clear();
        enemyShots.Clear();
        activeHormones.Clear();
        hearts.Clear();
        buffImage.enabled = false;
        hormonePickupImage.enabled = false;
        hormoneDurationFill.enabled = false;
        hormoneLabel.gameObject.SetActive(false);
    }

    private void PlayMusic(AudioClip clip)
    {
        musicSource.Stop();
        musicSource.clip = clip;
        musicSource.loop = clip == assets.MenuMusic || clip == assets.GameMusic;
        musicSource.Play();
    }

    private static Color ParseColor(string html)
    {
        ColorUtility.TryParseHtmlString(html, out var color);
        return color;
    }

    private static void SetGroupVisible(CanvasGroup group, bool visible)
    {
        group.alpha = visible ? 1f : 0f;
        group.interactable = visible;
        group.blocksRaycasts = visible;
    }

    private static void SetCenteredSize(RectTransform rect, float width, float height)
    {
        rect.anchorMin = Vector2.one * 0.5f;
        rect.anchorMax = Vector2.one * 0.5f;
        rect.pivot = Vector2.one * 0.5f;
        rect.sizeDelta = Vector2.right * width + Vector2.up * height;
    }

    private CanvasGroup CreateGroup(string name, RectTransform parent)
    {
        var groupObject = new GameObject(name);
        groupObject.transform.SetParent(parent, false);
        var rect = groupObject.AddComponent<RectTransform>();
        rect.anchorMin = Vector2.zero;
        rect.anchorMax = Vector2.one;
        rect.offsetMin = Vector2.zero;
        rect.offsetMax = Vector2.zero;
        return groupObject.AddComponent<CanvasGroup>();
    }

    private RectTransform CreateRect(string name, RectTransform parent)
    {
        var rectObject = new GameObject(name);
        rectObject.transform.SetParent(parent, false);
        var rect = rectObject.AddComponent<RectTransform>();
        rect.anchorMin = Vector2.zero;
        rect.anchorMax = Vector2.one;
        rect.offsetMin = Vector2.zero;
        rect.offsetMax = Vector2.zero;
        return rect;
    }

    private Image CreateImage(string name, RectTransform parent, Sprite sprite)
    {
        var imageObject = new GameObject(name);
        imageObject.transform.SetParent(parent, false);
        var image = imageObject.AddComponent<Image>();
        image.sprite = sprite;
        image.SetNativeSize();
        return image;
    }

    private TMP_Text CreateText(string name, RectTransform parent, float fontSize)
    {
        var textObject = new GameObject(name);
        textObject.transform.SetParent(parent, false);
        var text = textObject.AddComponent<TextMeshProUGUI>();
        text.fontSize = fontSize;
        text.color = Color.white;
        text.text = string.Empty;
        SetCenteredSize(text.rectTransform, 220f, 30f);
        return text;
    }

    private Vector2 ScreenToCanvas(float x, float y)
    {
        return Vector2.right * (x - ReferenceWidth * 0.5f) + Vector2.up * (y - ReferenceHeight * 0.5f);
    }

    private float RandomRange(float min, float max)
    {
        return min + (float)random.NextDouble() * (max - min);
    }

    private enum GameState
    {
        Menu,
        Mission,
        Battle,
        Ending,
    }

    private sealed class PlayerState
    {
        public float speed;
        public float damage;
        public int life;
        public float x;
        public float y;
        public float shotCooldown;
        public float shotSpeed;
        public bool charging;
        public float chargingTime;
        public bool directionRight;
        public int runIndex;
        public bool invisible;
        public float invisibleCooldown;
        public int chargeLevel;
    }

    private sealed class EnemyState
    {
        public float health;
        public float x;
        public float y;
        public int level;
        public float shotSpeed;
        public int choice;
        public float attackFrame;
        public float patternFrame;
        public float patternAccumulator;
        public int spiralIndex;
        public float tempTheta;
        public Sprite phaseSprite;
    }

    private sealed class ProjectileState
    {
        public float x;
        public float y;
        public float theta;
        public int level;
        public int pattern;
        public float holdFrames;
        public float speed;
        public Image image;
    }

    private sealed class HormonePickupState
    {
        public float cooldown;
        public int hormoneIndex;
        public float x;
        public float y;
    }

    private sealed class HormoneEffect
    {
        public int hormoneIndex;
        public float remaining;
    }

    private sealed class HormoneDefinition
    {
        public readonly string name;
        public readonly float damage;
        public readonly float speed;
        public readonly float shotSpeed;
        public readonly int life;

        public HormoneDefinition(string name, float damage, float speed, float shotSpeed, int life)
        {
            this.name = name;
            this.damage = damage;
            this.speed = speed;
            this.shotSpeed = shotSpeed;
            this.life = life;
        }
    }

    [Serializable]
    private sealed class AssetSources
    {
        public Texture2D buff;
        public Texture2D cursor;
        public Texture2D heart;
        public Texture2D menu;
        public Texture2D mission;
        public Texture2D youWin;
        public Texture2D gameOver;
        public Texture2D tileGreen;
        public Texture2D playerStanding;
        public Texture2D playerRun1;
        public Texture2D playerRun2;
        public Texture2D playerRun3;
        public Texture2D charge1;
        public Texture2D charge2;
        public Texture2D charge3;
        public Texture2D charge4;
        public Texture2D shot1;
        public Texture2D shot2;
        public Texture2D shot3;
        public Texture2D shot4;
        public Texture2D hormone1;
        public Texture2D hormone2;
        public Texture2D hormone3;
        public Texture2D hormone4;
        public Texture2D hormone5;
        public Texture2D hormone6;
        public Texture2D hormone7;
        public Texture2D hormone8;
        public Texture2D hormone9;
        public Texture2D hormone10;
        public Texture2D enemyIdle;
        public Texture2D enemyCharge;
        public Texture2D enemyReady;
        public Texture2D enemyShoot;
        public Texture2D enemyTeleport;
        public Texture2D enemyShot;
        public AudioClip menuMusic;
        public AudioClip gameMusic;
        public AudioClip endingMusic;
    }

    private sealed class AssetBank
    {
        public readonly Sprite White;
        public readonly Sprite Buff;
        public readonly Sprite Cursor;
        public readonly Sprite Heart;
        public readonly Sprite Menu;
        public readonly Sprite Mission;
        public readonly Sprite YouWin;
        public readonly Sprite GameOver;
        public readonly Sprite TileGreen;
        public readonly Sprite PlayerStandingRight;
        public readonly Sprite PlayerStandingLeft;
        public readonly Sprite[] PlayerRunRight;
        public readonly Sprite[] PlayerRunLeft;
        public readonly Sprite[] PlayerChargeRight;
        public readonly Sprite[] PlayerChargeLeft;
        public readonly Sprite[] PlayerShots;
        public readonly Sprite[] Hormones;
        public readonly Sprite EnemyIdle;
        public readonly Sprite EnemyCharge;
        public readonly Sprite EnemyReady;
        public readonly Sprite EnemyShoot;
        public readonly Sprite EnemyTeleport;
        public readonly Sprite EnemyShot;
        public readonly AudioClip MenuMusic;
        public readonly AudioClip GameMusic;
        public readonly AudioClip EndingMusic;

        public AssetBank(AssetSources source)
        {
            White = CreateSprite(CreateWhiteTexture());
            Buff = LoadSprite(source.buff);
            Cursor = LoadSprite(source.cursor);
            Heart = LoadSprite(source.heart);
            Menu = LoadSprite(source.menu);
            Mission = LoadSprite(source.mission);
            YouWin = LoadSprite(source.youWin);
            GameOver = LoadSprite(source.gameOver);
            TileGreen = LoadSprite(source.tileGreen);
            PlayerStandingRight = LoadSprite(source.playerStanding);
            PlayerStandingLeft = LoadSprite(source.playerStanding, true);
            PlayerRunRight = new[]
            {
                LoadSprite(source.playerRun1),
                LoadSprite(source.playerRun2),
                LoadSprite(source.playerRun3),
                LoadSprite(source.playerRun2),
            };
            PlayerRunLeft = new[]
            {
                LoadSprite(source.playerRun1, true),
                LoadSprite(source.playerRun2, true),
                LoadSprite(source.playerRun3, true),
                LoadSprite(source.playerRun2, true),
            };
            PlayerChargeRight = new[]
            {
                LoadSprite(source.charge1),
                LoadSprite(source.charge2),
                LoadSprite(source.charge3),
                LoadSprite(source.charge4),
            };
            PlayerChargeLeft = new[]
            {
                LoadSprite(source.charge1, true),
                LoadSprite(source.charge2, true),
                LoadSprite(source.charge3, true),
                LoadSprite(source.charge4, true),
            };
            PlayerShots = new[]
            {
                LoadSprite(source.shot1, false, 0f, 2f / 3f),
                LoadSprite(source.shot2, false, 0f, 2f / 3f),
                LoadSprite(source.shot3, false, 0f, 2f / 3f),
                LoadSprite(source.shot4, false, 0f, 2f / 3f),
            };
            Hormones = new[]
            {
                LoadSprite(source.hormone1, false, -45f),
                LoadSprite(source.hormone2, false, -45f),
                LoadSprite(source.hormone3, false, -45f),
                LoadSprite(source.hormone4, false, -45f),
                LoadSprite(source.hormone5, false, -45f),
                LoadSprite(source.hormone6, false, -45f),
                LoadSprite(source.hormone7, false, -45f),
                LoadSprite(source.hormone8, false, -45f),
                LoadSprite(source.hormone9, false, -45f),
                LoadSprite(source.hormone10, false, -45f),
            };
            EnemyIdle = LoadSprite(source.enemyIdle);
            EnemyCharge = LoadSprite(source.enemyCharge);
            EnemyReady = LoadSprite(source.enemyReady);
            EnemyShoot = LoadSprite(source.enemyShoot);
            EnemyTeleport = LoadSprite(source.enemyTeleport);
            EnemyShot = LoadSprite(source.enemyShot);
            MenuMusic = source.menuMusic;
            GameMusic = source.gameMusic;
            EndingMusic = source.endingMusic;
        }

        private Sprite LoadSprite(Texture2D texture, bool flipX = false, float rotation = 0f, float scale = 1f)
        {
            var prepared = texture;

            if (flipX || Mathf.Abs(rotation) > 0.001f || Mathf.Abs(scale - 1f) > 0.001f)
            {
                prepared = TransformTexture(texture, flipX, rotation, scale);
            }

            return CreateSprite(prepared);
        }

        private static Texture2D CreateWhiteTexture()
        {
            var texture = new Texture2D(1, 1, TextureFormat.RGBA32, false);
            texture.SetPixel(0, 0, Color.white);
            texture.Apply();
            return texture;
        }

        private static Sprite CreateSprite(Texture2D texture)
        {
            return Sprite.Create(
                texture,
                Rect.MinMaxRect(0f, 0f, texture.width, texture.height),
                Vector2.one * 0.5f,
                1f);
        }

        private static Texture2D TransformTexture(Texture2D source, bool flipX, float rotation, float scale)
        {
            var radians = rotation * Mathf.Deg2Rad;
            var cos = Mathf.Cos(radians);
            var sin = Mathf.Sin(radians);
            var width = Mathf.Max(1, Mathf.RoundToInt(source.width * scale));
            var height = Mathf.Max(1, Mathf.RoundToInt(source.height * scale));
            var transformed = new Texture2D(width, height, TextureFormat.RGBA32, false);
            var centerX = (source.width - 1f) * 0.5f;
            var centerY = (source.height - 1f) * 0.5f;
            var targetCenterX = (width - 1f) * 0.5f;
            var targetCenterY = (height - 1f) * 0.5f;

            for (var y = 0; y < height; y++)
            {
                for (var x = 0; x < width; x++)
                {
                    var scaledX = (x - targetCenterX) / scale;
                    var scaledY = (y - targetCenterY) / scale;
                    var rotatedX = cos * scaledX + sin * scaledY;
                    var rotatedY = -sin * scaledX + cos * scaledY;
                    var sampleX = Mathf.RoundToInt(rotatedX + centerX);
                    var sampleY = Mathf.RoundToInt(rotatedY + centerY);
                    if (flipX)
                    {
                        sampleX = source.width - 1 - sampleX;
                    }

                    if (sampleX >= 0 && sampleY >= 0 && sampleX < source.width && sampleY < source.height)
                    {
                        transformed.SetPixel(x, y, source.GetPixel(sampleX, sampleY));
                    }
                    else
                    {
                        transformed.SetPixel(x, y, Color.clear);
                    }
                }
            }

            transformed.Apply();
            return transformed;
        }
    }
}
