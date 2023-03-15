import { Component, Input } from '@angular/core';

@Component({
  selector: 'task-type-icon',
  template: `
    <container-element [ngSwitch]="type">
      <nb-icon *ngSwitchCase="'catch_up'" icon="flash" status="warning" nbTooltip="Catch Up"></nb-icon>
      <nb-icon *ngSwitchCase="'time_range'" icon="calendar" status="primary" nbTooltip="Time Range"></nb-icon>
      <nb-icon *ngSwitchCase="'saved_posts'" icon="heart" status="danger" nbTooltip="Saved Posts"></nb-icon>
      <nb-icon *ngSwitchDefault icon="question-mark-circle"></nb-icon>
    </container-element>
  `,
})
export class TaskTypeIconComponent {
  @Input() type: String = 'pending'

  constructor() { }
}
