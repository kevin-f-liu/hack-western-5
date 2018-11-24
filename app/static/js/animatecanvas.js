class Robot {
	constructor(color, light, size, x, y, struct) {
		this.x = x;
		this.points = [];
		this.links = [];
		this.frame = 0;
		this.dir = 1;
		this.size = size;
		this.color = Math.round(color);
		this.light = light;
		// ---- create points ----
		for (const p of struct.points) {
			this.points.push(new Robot.Point(size * p.x + x, size * p.y + y, p.f));
		}
		// ---- create links ----
		for (const link of struct.links) {
			const p0 = this.points[link.p0];
			const p1 = this.points[link.p1];
			const dx = p0.x - p1.x;
			const dy = p0.y - p1.y;
			this.links.push(
				new Robot.Link(
					this,
					p0,
					p1,
					Math.sqrt(dx * dx + dy * dy),
					link.size * size / 3,
					link.lum,
					link.force,
					link.disk
				)
			);
		}
	}
	update() {
		if (++this.frame % 20 === 0) this.dir = -this.dir;
		if (
			dancerDrag &&
			this === dancerDrag &&
			this.size < 16 &&
			this.frame > 600
		) {
			dancerDrag = null;
			dancers.push(
				new Robot(
					this.color + 90,
					this.light * 1.25,
					this.size * 2,
					pointer.x,
					pointer.y - 100 * this.size * 2,
					struct
				)
			);
			dancers.sort(function(d0, d1) {
				return d0.size - d1.size;
			});
		}
		// ---- update links ----
		for (const link of this.links) link.update();
		// ---- update points ----
		for (const point of this.points) point.update(this);
		// ---- ground ----
		for (const link of this.links) {
			const p1 = link.p1;
			if (p1.y > canvas.height * ground - link.size * 0.5) {
				p1.y = canvas.height * ground - link.size * 0.5;
				p1.x -= p1.vx;
				p1.vx = 0;
				p1.vy = 0;
			}
		}
		// ---- screen limits ----
		if (this.points[1].x < 0) this.points[1].x = 0;
		else if (this.points[1].x > canvas.width) this.points[1].x = canvas.width;
	}
}
Robot.Link = class Link {
	constructor(parent, p0, p1, dist, size, light, force, disk) {
		this.p0 = p0;
		this.p1 = p1;
		this.distance = dist;
		this.size = size;
		this.light = light || 1.0;
		this.force = force || 0.5;
		this.color = `hsl(${parent.color}, 30%, ${parent.light * this.light}%)`;
		this.disk = disk;
	}
	update() {
		const p0 = this.p0;
		const p1 = this.p1;
		const dx = p1.x - p0.x;
		const dy = p1.y - p0.y;
		const dist = Math.sqrt(dx * dx + dy * dy);
		if (dist > 0.0) {
			const tw = p0.w + p1.w;
			const r1 = p1.w / tw;
			const r0 = p0.w / tw;
			const dz = (this.distance - dist) * this.force;
			const sx = dx / dist * dz;
			const sy = dy / dist * dz;
			p1.x += sx * r0;
			p1.y += sy * r0;
			p0.x -= sx * r1;
			p0.y -= sy * r1;
		}
		// ---- draw link ----
		if (this.size) {
			const w = this.size;
			const a = Math.atan2(dy, dx);
			const c = Math.cos(a);
			const s = Math.sin(a);
			if (this.disk) {
				ctx.setTransform(c, s, -s, c, p1.x + w * 0.25, p1.y + w * 0.25);
				ctx.beginPath();
				ctx.arc(0, 0, w * 0.5, 0, 2 * Math.PI);
				ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
				ctx.fill();
			} else {
				ctx.setTransform(c, s, -s, c, p0.x + w * 0.25, p0.y + w * 0.25);
				ctx.beginPath();
				ctx.lineCap = "round";
				ctx.lineWidth = w;
				ctx.beginPath();
				ctx.strokeStyle = "rgba(0, 0, 0, 0.5)";
				ctx.moveTo(0, 0);
				ctx.lineTo(dist, 0);
				ctx.stroke();
			}	
			if (this.disk) {
				ctx.setTransform(c, s, -s, c, p1.x, p1.y);
				ctx.beginPath();
				ctx.arc(0, 0, w * 0.5, 0, 2 * Math.PI);
				ctx.fillStyle = this.color;
				ctx.fill();
				ctx.fillStyle = "#000";
				ctx.fillRect(-w * 0.1, -w * 0.1, w * 0.2, w * 0.2);
			} else {
				ctx.setTransform(c, s, -s, c, p0.x, p0.y);
				ctx.beginPath();
				ctx.lineCap = "round";
				ctx.lineWidth = w;
				ctx.beginPath();
				ctx.strokeStyle = this.color;
				ctx.moveTo(0, 0);
				ctx.lineTo(dist, 0);
				ctx.stroke();
				ctx.fillStyle = "#000";
				ctx.fillRect(-w * 0.1, -w * 0.1, w * 0.2, w * 0.2);
				ctx.fillRect(dist - w * 0.1, -w * 0.1, w * 0.2, w * 0.2);
			}
		}
	}
};
Robot.Point = class Point {
	constructor(x, y, fn, w) {
		this.x = x;
		this.y = y;
		this.w = w || 0.5;
		this.fn = fn || null;
		this.px = x;
		this.py = y;
		this.vx = 0.0;
		this.vy = 0.0;
	}
	update (robot) {
		// ---- dragging ----
		if (robot === dancerDrag && this === pointDrag) {
			this.x += (pointer.x - this.x) * 0.1;
			this.y += (pointer.y - this.y) * 0.1;
		}
		// ---- dance ----
		if (robot !== dancerDrag) {
			this.fn && this.fn(16 * Math.sqrt(robot.size), robot.dir);
		}
		// ---- verlet integration ----
		this.vx = this.x - this.px;
		this.vy = this.y - this.py;
		this.px = this.x;
		this.py = this.y;
		this.vx *= 0.995;
		this.vy *= 0.995;
		this.x += this.vx;
		this.y += this.vy + 0.01;
	}
};
// ---- set canvas ----
const canvas = {
	init() {
		this.elem = document.querySelector("canvas");
		this.resize();
		window.addEventListener("resize", () => this.resize(), false);
		return this.elem.getContext("2d");
	},
	resize() {
		this.width = this.elem.width = this.elem.offsetWidth;
		this.height = this.elem.height = this.elem.offsetHeight;
		ground = this.height > 500 ? 0.85 : 1.0;
		for (let i = 0; i < dancers.length; i++) {
			dancers[i].x = (i + 2) * canvas.width / 9;
		}
	}
};
// ---- set pointer ----
const pointer = {
	init(canvas) {
		this.x = 0;
		this.y = 0;
		window.addEventListener("mousemove", e => this.move(e), false);
		canvas.elem.addEventListener("touchmove", e => this.move(e), false);
		window.addEventListener("mousedown", e => this.down(e), false);
		window.addEventListener("touchstart", e => this.down(e), false);
		window.addEventListener("mouseup", e => this.up(e), false);
		window.addEventListener("touchend", e => this.up(e), false);
	},
	down(e) {
		this.move(e);
		for (const dancer of dancers) {
			for (const point of dancer.points) {
				const dx = pointer.x - point.x;
				const dy = pointer.y - point.y;
				const d = Math.sqrt(dx * dx + dy * dy);
				if (d < 60) {
					dancerDrag = dancer;
					pointDrag = point;
					dancer.frame = 0;
				}
			}
		}
	},
	up(e) {
		dancerDrag = null;
	},
	move(e) {
		let touchMode = e.targetTouches,
			pointer;
		if (touchMode) {
			e.preventDefault();
			pointer = touchMode[0];
		} else pointer = e;
		this.x = pointer.clientX;
		this.y = pointer.clientY;
	}
};
// ---- init ----
const dancers = [];
let ground = 1.0;
const ctx = canvas.init();
pointer.init(canvas);
let dancerDrag = null;
let pointDrag = null;
// ---- dance ----
const dance = () => {
	ctx.save();
	for (let i = 0; i < dancers.length; i++) {
		const d0 = dancers[i];
		d0.update();
		// separation behavior
		for (let j = i + 1; j < dancers.length; j++) {
			const d1 = dancers[j];
			const minDist = Math.abs(d0.x - d1.x);
			const actDist = Math.abs(d0.points[2].x - d1.points[2].x);
			if (actDist < minDist * 0.8) {
				const d = minDist - actDist;
				if (d0.points[2].x < d1.points[2].x) {
					d0.points[2].x -= d * 0.001;
					d1.points[2].x += d * 0.001;
				} else {
					d0.points[2].x += d * 0.001;
					d1.points[2].x -= d * 0.001;
				}
			}
		}
	}
	ctx.restore();
}
// ---- main loop ----
const run = () => {
	requestAnimationFrame(run);
	ctx.clearRect(0, 0, canvas.width, canvas.height);
	ctx.fillStyle = "#222";
	ctx.fillRect(0, 0, canvas.width, canvas.height * 0.15);
	ctx.fillRect(0, canvas.height * 0.85, canvas.width, canvas.height * 0.15);
	dance();
};
// ---- robot structure ----
const struct = {
	points: [
		{
			x: 0,
			y: -4,
			f(s, d) {
				this.y -= 0.01 * s;
			}
		},
		{
			x: 0,
			y: -16,
			f(s, d) {
				this.y -= 0.02 * s * d;
			}
		},
		{
			x: 0,
			y: 12,
			f(s, d) {
				this.y += 0.02 * s * d;
			}
		},
		{ x: -12, y: 0 },
		{ x: 12, y: 0 },
		{
			x: -3,
			y: 34,
			f(s, d) {
				if (d > 0) {
					this.x += 0.01 * s;
					this.y -= 0.015 * s;
				} else {
					this.y += 0.02 * s;
				}
			}
		},
		{
			x: 3,
			y: 34,
			f(s, d) {
				if (d > 0) {
					this.y += 0.02 * s;
				} else {
					this.x -= 0.01 * s;
					this.y -= 0.015 * s;
				}
			}
		},
		{
			x: -28,
			y: 0,
			f(s, d) {
				this.x += this.vx * 0.025;
				this.y -= 0.001 * s;
			}
		},
		{
			x: 28,
			y: 0,
			f(s, d) {
				this.x += this.vx * 0.025;
				this.y -= 0.001 * s;
			}
		},
		{
			x: -3,
			y: 64,
			f(s, d) {
				this.y += 0.015 * s;
				if (d > 0) {
					this.y -= 0.01 * s;
				} else {
					this.y += 0.05 * s;
				}
			}
		},
		{
			x: 3,
			y: 64,
			f(s, d) {
				this.y += 0.015 * s;
				if (d > 0) {
					this.y += 0.05 * s;
				} else {
					this.y -= 0.01 * s;
				}
			}
		}
	],
	links: [
		{ p0: 3, p1: 7, size: 12, lum: 0.5 },
		{ p0: 1, p1: 3, size: 24, lum: 0.5 },
		{ p0: 1, p1: 0, size: 60, lum: 0.5, disk: 1 },
		{ p0: 5, p1: 9, size: 16, lum: 0.5 },
		{ p0: 2, p1: 5, size: 32, lum: 0.5 },
		{ p0: 1, p1: 2, size: 50, lum: 1 },
		{ p0: 6, p1: 10, size: 16, lum: 1.5 },
		{ p0: 2, p1: 6, size: 32, lum: 1.5 },
		{ p0: 4, p1: 8, size: 12, lum: 1.5 },
		{ p0: 1, p1: 4, size: 24, lum: 1.5 }
	]
};
// ---- instanciate robots ----
for (let i = 0; i < 6; i++) {
	dancers.push(
		new Robot(
			i * 360 / 7,
			80,
			4,
			(i + 2) * canvas.width / 9,
			canvas.height * ground - 300,
			struct
		)
	);
}
// ---- warm up ----
run();
